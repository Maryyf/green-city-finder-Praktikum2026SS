import hashlib
import hmac
import json
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta


DB_PATH = Path("database/user_profile.db")

PROFILE_FIELDS = [
    "beach",
    "nature",
    "outdoor",
    "historic",
    "culture",
    "nightlife",
    "food",
    "shopping",
    "low_cost",
    "low_carbon",
    "dry_weather",
]

PASSWORD_HASH_ITERATIONS = 120_000
PROFILE_DECAY_FACTOR = 0.8
DEFAULT_AVATAR = "👤"
SESSION_DAYS = 30


def profile_columns_sql(column_type: str = "REAL") -> str:
    return ",\n                ".join(
        f"{field} {column_type} NOT NULL DEFAULT 0"
        for field in PROFILE_FIELDS
    )


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def normalize_username(username: str, email: str = "") -> str:
    username = (username or "").strip()

    if not username and email:
        username = normalize_email(email).split("@")[0]

    if not username:
        username = "Traveller"

    return username[:40]


def normalize_avatar(avatar: str) -> str:
    avatar = (avatar or "").strip()
    return avatar[:8] if avatar else DEFAULT_AVATAR


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("password cannot be empty")

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    ).hex()

    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt}${password_hash}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    if not password or not stored_password_hash:
        return False

    try:
        algorithm, iterations, salt, expected_hash = stored_password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()

    return hmac.compare_digest(actual_hash, expected_hash)


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_names(conn: sqlite3.Connection, table_name: str) -> set[str]:
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {column["name"] for column in columns}


def migrate_users_add_profile_metadata(conn: sqlite3.Connection) -> None:
    columns = _column_names(conn, "users")

    if "username" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN username TEXT")

    if "avatar" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN avatar TEXT")

    rows = conn.execute(
        """
        SELECT id, email, username, avatar
        FROM users
        """
    ).fetchall()

    for row in rows:
        username = normalize_username(row["username"], row["email"])
        avatar = normalize_avatar(row["avatar"])

        conn.execute(
            """
            UPDATE users
            SET username = ?,
                avatar = ?
            WHERE id = ?
            """,
            (username, avatar, row["id"]),
        )


def migrate_user_profiles_to_real(conn: sqlite3.Connection) -> None:
    columns = conn.execute("PRAGMA table_info(user_profiles)").fetchall()

    if not columns:
        return

    column_types = {
        column["name"]: (column["type"] or "").upper()
        for column in columns
    }

    if all(column_types.get(field) == "REAL" for field in PROFILE_FIELDS):
        return

    profile_field_list = ", ".join(PROFILE_FIELDS)
    cast_profile_fields = ", ".join(
        f"CAST({field} AS REAL)"
        for field in PROFILE_FIELDS
    )

    conn.execute("""
        CREATE TABLE user_profiles_new (
            user_id INTEGER PRIMARY KEY,
            """ + profile_columns_sql("REAL") + """,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.execute(f"""
        INSERT INTO user_profiles_new (
            user_id,
            {profile_field_list},
            updated_at
        )
        SELECT
            user_id,
            {cast_profile_fields},
            updated_at
        FROM user_profiles
    """)

    conn.execute("DROP TABLE user_profiles")
    conn.execute("ALTER TABLE user_profiles_new RENAME TO user_profiles")


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                avatar TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        migrate_users_add_profile_metadata(conn)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                """ + profile_columns_sql("REAL") + """,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        migrate_user_profiles_to_real(conn)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS favourites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                starting_point TEXT,
                context_params TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def create_user(
    email: str,
    password: str,
    username: str | None = None,
    avatar: str | None = None,
) -> int:
    email = normalize_email(email)

    if not email:
        raise ValueError("email cannot be empty")

    if not password:
        raise ValueError("password cannot be empty")

    username = normalize_username(username or "", email)
    avatar = normalize_avatar(avatar or DEFAULT_AVATAR)

    init_db()

    password_hash = hash_password(password)
    created_at = now_iso()

    with get_connection() as conn:
        existing_user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if existing_user:
            raise ValueError("email already registered")

        cursor = conn.execute(
            """
            INSERT INTO users (
                email,
                username,
                avatar,
                password_hash,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (email, username, avatar, password_hash, created_at),
        )

        user_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO user_profiles (
                user_id,
                updated_at
            ) VALUES (?, ?)
            """,
            (user_id, created_at),
        )

        return user_id


def authenticate_user(email: str, password: str) -> int | None:
    user = get_user_by_email(email)

    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user["id"]


def create_session(user_id: int, days: int = SESSION_DAYS) -> str:
    if user_id is None:
        raise ValueError("user_id cannot be empty")

    init_db()

    token = secrets.token_urlsafe(32)
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=days)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                token,
                user_id,
                created_at,
                expires_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                token,
                user_id,
                created_at.isoformat(timespec="seconds"),
                expires_at.isoformat(timespec="seconds"),
            ),
        )

    return token


def get_user_id_by_session_token(token: str | None) -> int | None:
    token = (token or "").strip()

    if not token:
        return None

    init_db()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT token, user_id, expires_at
            FROM sessions
            WHERE token = ?
            """,
            (token,),
        ).fetchone()

        if not row:
            return None

        try:
            expires_at = datetime.fromisoformat(row["expires_at"])
        except ValueError:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None

        if expires_at < datetime.now():
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None

        return row["user_id"]


def delete_session(token: str | None) -> None:
    token = (token or "").strip()

    if not token:
        return

    init_db()

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM sessions WHERE token = ?",
            (token,),
        )


def get_user_id_by_email(email: str) -> int | None:
    email = normalize_email(email)

    if not email:
        raise ValueError("email cannot be empty")

    init_db()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if row:
            return row["id"]

        return None


def get_user_by_email(email: str) -> dict | None:
    email = normalize_email(email)

    if not email:
        raise ValueError("email cannot be empty")

    init_db()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    return row_to_dict(row)


def get_user_by_id(user_id: int) -> dict | None:
    if user_id is None:
        return None

    init_db()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    return row_to_dict(row)


def get_user_public_profile(user_id: int) -> dict:
    user = get_user_by_id(user_id)

    if not user:
        return {
            "username": "Traveller",
            "avatar": DEFAULT_AVATAR,
            "email": "",
        }

    return {
        "username": normalize_username(user.get("username"), user.get("email", "")),
        "avatar": normalize_avatar(user.get("avatar")),
        "email": user.get("email", ""),
    }


def update_user_metadata(
    user_id: int,
    username: str | None = None,
    avatar: str | None = None,
) -> None:
    if user_id is None:
        raise ValueError("user_id cannot be empty")

    init_db()

    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("user not found")

    username = normalize_username(username or user.get("username"), user.get("email", ""))
    avatar = normalize_avatar(avatar or user.get("avatar"))

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE users
            SET username = ?,
                avatar = ?
            WHERE id = ?
            """,
            (username, avatar, user_id),
        )


def get_user_profile(user_id: int) -> dict:
    init_db()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    profile = row_to_dict(row)

    if profile is None:
        return {}

    profile.pop("user_id", None)
    profile.pop("updated_at", None)

    return profile


def save_favourite(
    user_id: int,
    query: str,
    starting_point: str,
    context_params: dict,
    recommendation: str,
) -> int:
    init_db()

    created_at = now_iso()
    context_params_json = json.dumps(context_params, ensure_ascii=False)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO favourites (
                user_id,
                query,
                starting_point,
                context_params,
                recommendation,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                query,
                starting_point,
                context_params_json,
                recommendation,
                created_at,
            ),
        )

        return cursor.lastrowid


def update_user_profile(
    user_id: int,
    profile_update: dict,
    decay_factor: float = PROFILE_DECAY_FACTOR,
) -> None:
    init_db()
    current_time = now_iso()

    updates = {
        field: float(profile_update.get(field, 0) or 0)
        for field in PROFILE_FIELDS
    }

    assignments = [
        f"{field} = ({field} * ?) + ?"
        for field in PROFILE_FIELDS
    ]

    values = []

    for field in PROFILE_FIELDS:
        values.append(decay_factor)
        values.append(updates[field])

    values.append(current_time)
    values.append(user_id)

    sql = f"""
        UPDATE user_profiles
        SET {", ".join(assignments)},
            updated_at = ?
        WHERE user_id = ?
    """

    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO user_profiles (
                user_id,
                updated_at
            ) VALUES (?, ?)
            """,
            (user_id, current_time),
        )
        conn.execute(sql, values)


def get_user_favourites(user_id: int) -> list[dict]:
    init_db()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM favourites
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()

    favourites = []

    for row in rows:
        item = row_to_dict(row)
        item["context_params"] = json.loads(item["context_params"])
        favourites.append(item)

    return favourites
