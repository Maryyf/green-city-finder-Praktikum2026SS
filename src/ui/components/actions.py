import re
from html import escape
from typing import Optional

import gradio as gr

from src.pipeline import pipeline
from src.user_profile.db import (
    PROFILE_FIELDS,
    create_user,
    authenticate_user,
    create_session,
    get_user_id_by_session_token,
    delete_session,
    get_user_profile,
    get_user_public_profile,
    save_favourite,
    update_user_profile,
    update_user_metadata,
    get_user_favourites,
    delete_favourite,
)
from src.user_profile.profile_extractor import extract_profile_from_query


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

AVATAR_OPTIONS = ["🌿", "🌍", "🏔️", "🏖️", "🚆", "🎒", "👤"]

PROFILE_LABELS = {
    "beach_coast": "Beach & coast",
    "mountains_hiking": "Mountains & hiking",
    "nature_wildlife": "Nature & wildlife",
    "winter_sports": "Winter sports",
    "water_sports": "Water sports",
    "history_heritage": "History & heritage",
    "arts_museums": "Arts & museums",
    "architecture": "Architecture",
    "local_culture": "Local culture",
    "food_drink": "Food & drink",
    "nightlife": "Nightlife",
    "music_festivals": "Music & festivals",
    "shopping_markets": "Shopping & markets",
    "wellness_relaxation": "Wellness & relaxation",
    "major_city": "Major cities",
    "small_town": "Small towns",
    "hidden_gems": "Hidden gems",
    "budget": "Budget travel",
    "luxury": "Luxury travel",
    "dry_weather": "Dry weather",
    "low_carbon": "Low carbon",
}

PROFILE_COLOR_CLASSES = {
    "beach_coast": "bar-beach",
    "mountains_hiking": "bar-outdoor",
    "nature_wildlife": "bar-nature",
    "winter_sports": "bar-outdoor",
    "water_sports": "bar-beach",
    "history_heritage": "bar-historic",
    "arts_museums": "bar-culture",
    "architecture": "bar-historic",
    "local_culture": "bar-culture",
    "food_drink": "bar-food",
    "nightlife": "bar-nightlife",
    "music_festivals": "bar-nightlife",
    "shopping_markets": "bar-shopping",
    "wellness_relaxation": "bar-nature",
    "major_city": "bar-culture",
    "small_town": "bar-nature",
    "hidden_gems": "bar-low-carbon",
    "budget": "bar-low-cost",
    "luxury": "bar-shopping",
    "dry_weather": "bar-dry-weather",
    "low_carbon": "bar-low-carbon",
}


def clear(*args):
    return tuple([None] * len(args))


def _normalize_avatar_choice(avatar: Optional[str]) -> str:
    avatar = (avatar or "").strip()
    return avatar if avatar in AVATAR_OPTIONS else "👤"


def register_user(
    email: str,
    password: str,
    username: Optional[str] = None,
    avatar: Optional[str] = None,
):
    normalized_email = (email or "").strip().lower()
    username = (username or "").strip()
    avatar = _normalize_avatar_choice(avatar)

    if not EMAIL_PATTERN.fullmatch(normalized_email):
        return None, "Registration failed: enter a valid email address.", ""

    if len(username) > 40:
        return None, "Registration failed: username must be 40 characters or fewer.", ""

    if len(password or "") < 8:
        return None, "Registration failed: password must contain at least 8 characters.", ""

    try:
        user_id = create_user(
            normalized_email,
            password,
            username=username,
            avatar=avatar,
        )
        session_token = create_session(user_id)
        return user_id, f"Registered and logged in as {normalized_email}", session_token
    except ValueError as exc:
        return None, f"Registration failed: {exc}", ""
    except Exception:
        return None, "Registration failed: an unexpected error occurred.", ""


def login_user(email: str, password: str):
    normalized_email = (email or "").strip().lower()

    if not normalized_email or not password:
        return None, "Login failed: enter both email and password.", ""

    try:
        user_id = authenticate_user(normalized_email, password)

        if user_id is None:
            return None, "Login failed: invalid email or password.", ""

        session_token = create_session(user_id)
        return user_id, f"Logged in as {normalized_email}", session_token
    except Exception:
        return None, "Login failed: an unexpected error occurred.", ""


def restore_session_from_cookie(session_token: Optional[str]):
    session_token = (session_token or "").strip()

    user_id = get_user_id_by_session_token(session_token)

    if user_id is None:
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            "",
            "",
            gr.update(value="👤"),
        )

    user = get_user_display(user_id)

    return (
        user_id,
        gr.update(visible=False),
        gr.update(visible=True),
        "",
        session_token,
        gr.update(value=user.get("avatar", "👤")),
    )



def logout_user(session_token: Optional[str]):
    """
    Remove the current browser session from the database.

    The browser cookie is cleared by frontend JS after this function returns.
    """
    try:
        delete_session(session_token)
    except Exception:
        # Logout should still continue even if the token is already missing.
        pass

    return (
        None,
        gr.update(visible=True),
        gr.update(visible=False),
        "",
        "",
        gr.update(value="👤"),
        gr.update(visible=False),
    )

def get_user_display(current_user_id: Optional[int]) -> dict:
    if current_user_id is None:
        return {
            "username": "Guest",
            "avatar": "👤",
            "email": "",
        }

    return get_user_public_profile(current_user_id)


def render_profile_header(current_user_id: Optional[int]) -> str:
    user = get_user_display(current_user_id)

    username = escape(user.get("username") or "Traveller")
    avatar = escape(user.get("avatar") or "👤")
    email = escape(user.get("email") or "")

    subtitle = (
        "Your saved recommendations gradually shape this profile."
        if current_user_id is not None
        else "Please sign in to view your travel profile."
    )

    email_html = f'<div class="profile-card-email">{email}</div>' if email else ""

    return f"""
    <div class="profile-card-header">
        <div class="profile-card-avatar">{avatar}</div>
        <div>
            <div class="profile-card-title">{username}</div>
            {email_html}
            <div class="profile-card-subtitle">{subtitle}</div>
        </div>
    </div>
    """


def _travel_preference_title() -> str:
    return """
    <div class="travel-preference-title">Travel Preference</div>
    """


def render_profile_bars(current_user_id: Optional[int]) -> str:
    if current_user_id is None:
        return f"""
        {_travel_preference_title()}
        <div class="profile-empty-state">
            Sign in first to view your travel profile.
        </div>
        """

    profile = get_user_profile(current_user_id)

    if not profile:
        return f"""
        {_travel_preference_title()}
        <div class="profile-empty-state">
            No profile found yet. Save recommendations to build your profile.
        </div>
        """

    numeric_profile = {
        field: max(float(profile.get(field, 0) or 0), 0.0)
        for field in PROFILE_FIELDS
    }

    ranked_profile = sorted(
        (
            (field, score)
            for field, score in numeric_profile.items()
            if score > 0
        ),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    max_score = ranked_profile[0][1] if ranked_profile else 0

    if max_score <= 0:
        return f"""
        {_travel_preference_title()}
        <div class="profile-empty-state">
            Your profile is empty. Save recommendations to build personalised preference bars.
        </div>
        """

    rows = []

    for field, score in ranked_profile:
        label = PROFILE_LABELS.get(field, field.replace("_", " ").title())
        color_class = PROFILE_COLOR_CLASSES.get(field, "bar-default")

        width = 0 if score <= 0 else max(8, round(score / max_score * 100, 1))
        score_text = f"{score:.2f}"

        rows.append(
            f"""
            <div class="profile-bar-row">
                <div class="profile-bar-meta">
                    <span class="profile-bar-label">{escape(label)}</span>
                    <span class="profile-bar-score">{score_text}</span>
                </div>
                <div class="profile-bar-track">
                    <div class="profile-bar-fill {color_class}" style="width: {width}%"></div>
                </div>
            </div>
            """
        )

    return f"""
    {_travel_preference_title()}
    <div class="profile-bars">
        {''.join(rows)}
    </div>
    """


def update_username(current_user_id: Optional[int], new_username: Optional[str]):
    if current_user_id is None:
        return (
            render_profile_header(current_user_id),
            "❌ Please sign in first.",
            "",
        )

    new_username = (new_username or "").strip()

    if not new_username:
        return (
            render_profile_header(current_user_id),
            "❌ Username cannot be empty.",
            new_username,
        )

    if len(new_username) > 40:
        return (
            render_profile_header(current_user_id),
            "❌ Username must be 40 characters or fewer.",
            new_username,
        )

    try:
        update_user_metadata(
            user_id=current_user_id,
            username=new_username,
        )
    except Exception as exc:
        return (
            render_profile_header(current_user_id),
            f"❌ Failed to update username: {escape(str(exc))}",
            new_username,
        )

    user = get_user_display(current_user_id)

    return (
        render_profile_header(current_user_id),
        f"✅ Username updated to {escape(user.get('username', new_username))}.",
        user.get("username", new_username),
    )


def update_avatar(current_user_id: Optional[int], new_avatar: Optional[str]):
    if current_user_id is None:
        return (
            render_profile_header(current_user_id),
            "❌ Please sign in first.",
            "👤",
            gr.update(value="👤"),
        )

    new_avatar = _normalize_avatar_choice(new_avatar)

    try:
        update_user_metadata(
            user_id=current_user_id,
            avatar=new_avatar,
        )
    except Exception as exc:
        return (
            render_profile_header(current_user_id),
            f"❌ Failed to update avatar: {escape(str(exc))}",
            new_avatar,
            gr.update(value=new_avatar),
        )

    user = get_user_display(current_user_id)
    avatar = user.get("avatar", new_avatar)

    return (
        render_profile_header(current_user_id),
        f"✅ Avatar updated to {escape(avatar)}.",
        avatar,
        gr.update(value=avatar),
    )




def render_markdown_like_html(text: str) -> str:
    """
    Render the saved raw Markdown-like recommendation text inside bookmark HTML.

    The main recommendation output uses gr.Markdown directly. Bookmarks are
    rendered inside HTML <details> blocks, so this helper converts the most
    common Markdown markers into lightweight HTML without using card styling.
    """
    text = escape(text or "")

    # Bold: **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    lines = text.splitlines()
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        bullet_match = re.match(r"^\*\s+(.*)$", stripped)

        if bullet_match:
            if not in_list:
                html_lines.append("<ul class='bookmark-markdown-list'>")
                in_list = True

            html_lines.append(f"<li>{bullet_match.group(1)}</li>")
            continue

        if in_list:
            html_lines.append("</ul>")
            in_list = False

        if not stripped:
            html_lines.append("<br>")
        elif re.match(r"^\d+\.\s+", stripped):
            html_lines.append(f"<h4 class='bookmark-markdown-heading'>{stripped}</h4>")
        else:
            html_lines.append(f"<p>{stripped}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


BOOKMARK_ROW_LIMIT = 40


def _shorten_text(text: Optional[str], max_length: int = 72) -> str:
    text = " ".join((text or "").split())

    if len(text) <= max_length:
        return text

    return text[: max_length - 1].rstrip() + "…"


def _render_bookmark_card(bookmark: dict) -> str:
    bookmark_id = escape(str(bookmark.get("id", "")))
    query = escape(bookmark.get("query") or "Untitled travel request")
    query_short = escape(_shorten_text(bookmark.get("query") or "Untitled travel request", 92))
    starting_point = escape(bookmark.get("starting_point") or "Not specified")
    created_at = escape(bookmark.get("created_at") or "")
    recommendation_html = render_markdown_like_html(bookmark.get("recommendation") or "")

    context_params = bookmark.get("context_params") or {}
    context_rows = []

    for key, value in context_params.items():
        if value is None or value == "":
            continue

        context_rows.append(
            f"""
            <div class="bookmark-context-row">
                <span>{escape(str(key).replace("_", " ").title())}</span>
                <strong>{escape(str(value))}</strong>
            </div>
            """
        )

    context_html = (
        f"""
        <div class="bookmark-context">
            {''.join(context_rows)}
        </div>
        """
        if context_rows
        else ""
    )

    return f"""
    <details class="bookmark-expand-card">
        <summary class="bookmark-summary">
            <div class="bookmark-summary-main">
                <div class="bookmark-summary-title">
                    Bookmark #{bookmark_id}
                </div>
                <div class="bookmark-summary-query">
                    {query_short}
                </div>
                <div class="bookmark-summary-meta">
                    <span>Starting point: <strong>{starting_point}</strong></span>
                    <span>{created_at}</span>
                </div>
            </div>
            <span class="bookmark-summary-icon">⌄</span>
        </summary>

        <div class="bookmark-detail-card">
            <div class="bookmark-detail-meta">
                <span>Saved recommendation</span>
                <strong>{created_at}</strong>
            </div>

            <div class="bookmark-detail-title">
                {query}
            </div>

            <div class="bookmark-detail-start">
                Starting point: <strong>{starting_point}</strong>
            </div>

            {context_html}

            <div class="bookmark-result-title">Recommendation result</div>
            <div class="bookmark-result-body bookmark-result-markdown">
                {recommendation_html}
            </div>
        </div>
    </details>
    """


def _bookmark_row_updates(current_user_id: Optional[int]) -> list:
    """
    Return updates for fixed Gradio bookmark rows.

    Each row has:
    1. row visibility update
    2. HTML content value
    3. hidden state bookmark id

    Real Gradio buttons are used beside each row, so Delete reliably triggers
    Python instead of relying on onclick inside gr.HTML.
    """
    updates = []

    if current_user_id is None:
        favourites = []
    else:
        favourites = get_user_favourites(current_user_id)

    visible_favourites = favourites[:BOOKMARK_ROW_LIMIT]

    for bookmark in visible_favourites:
        updates.extend(
            [
                gr.update(visible=True),
                _render_bookmark_card(bookmark),
                int(bookmark.get("id")),
            ]
        )

    hidden_count = BOOKMARK_ROW_LIMIT - len(visible_favourites)

    for _ in range(hidden_count):
        updates.extend(
            [
                gr.update(visible=False),
                "",
                None,
            ]
        )

    return updates


def _bookmarks_status_html(current_user_id: Optional[int], message: str = "") -> str:
    if message:
        return f"""
        <div class="bookmark-action-status">
            {escape(message)}
        </div>
        """

    if current_user_id is None:
        return """
        <div class="bookmark-empty-state">
            Please sign in first to view your bookmarks.
        </div>
        """

    favourites = get_user_favourites(current_user_id)

    if not favourites:
        return """
        <div class="bookmark-empty-state">
            You have no bookmarks yet. Generate a recommendation and click
            <strong>Save to favourites</strong> to add one here.
        </div>
        """

    limit_note = ""

    if len(favourites) > BOOKMARK_ROW_LIMIT:
        limit_note = f"""
        <br>
        Showing the latest {BOOKMARK_ROW_LIMIT} bookmarks.
        """

    return f"""
    <div class="bookmark-helper">
        Click any bookmark to expand its saved result. Click it again to collapse it.
        Use the <strong>Delete</strong> button beside a bookmark to remove it from the database.
        {limit_note}
    </div>
    """


def open_bookmarks_page(current_user_id: Optional[int]):
    """
    Open the separate Bookmarks page.
    """
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        _bookmarks_status_html(current_user_id),
        *_bookmark_row_updates(current_user_id),
    )


def refresh_bookmarks_page(current_user_id: Optional[int]):
    """Refresh bookmark content without changing page visibility."""
    return (
        _bookmarks_status_html(current_user_id),
        *_bookmark_row_updates(current_user_id),
    )


def back_to_recommendation_page():
    """
    Return from the Bookmarks page to the recommendation page.
    """
    hidden_rows = []

    for _ in range(BOOKMARK_ROW_LIMIT):
        hidden_rows.extend(
            [
                gr.update(visible=False),
                "",
                None,
            ]
        )

    return (
        gr.update(visible=True),
        gr.update(visible=False),
        """
        <div class="bookmark-helper">
            Select <strong>My bookmarks</strong> again to view saved recommendations.
        </div>
        """,
        *hidden_rows,
    )


def delete_bookmark(current_user_id: Optional[int], bookmark_id: Optional[int]):
    """
    Delete one bookmark from the database and refresh the visible bookmark rows.
    """
    if current_user_id is None:
        return (
            _bookmarks_status_html(current_user_id, "❌ Please sign in first."),
            *_bookmark_row_updates(current_user_id),
        )

    if bookmark_id is None:
        return (
            _bookmarks_status_html(current_user_id, "❌ Could not identify the bookmark to delete."),
            *_bookmark_row_updates(current_user_id),
        )

    try:
        bookmark_id = int(bookmark_id)
    except (TypeError, ValueError):
        return (
            _bookmarks_status_html(current_user_id, "❌ Could not identify the bookmark to delete."),
            *_bookmark_row_updates(current_user_id),
        )

    deleted = delete_favourite(
        user_id=current_user_id,
        favourite_id=bookmark_id,
    )

    if not deleted:
        return (
            _bookmarks_status_html(current_user_id, "❌ Bookmark not found or already deleted."),
            *_bookmark_row_updates(current_user_id),
        )

    return (
        _bookmarks_status_html(current_user_id, f"✅ Bookmark #{bookmark_id} deleted."),
        *_bookmark_row_updates(current_user_id),
    )

def save_recommendation(
    current_user_id: Optional[int],
    query_text: str,
    starting_point: Optional[str],
    cost_preference: Optional[str],
    temporary_events: Optional[bool],
    weather: Optional[bool],
    carbon_footprint_preference: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    recommendation: str,
):
    if current_user_id is None:
        return "Please log in before saving."

    if not recommendation:
        return "Please generate a recommendation before saving."

    context_params = {
        "cost_preference": cost_preference,
        "temporary_events": temporary_events,
        "weather": weather,
        "weather_preference": "Prefer dry weather" if weather else None,
        "carbon_footprint_preference": carbon_footprint_preference,
        "start_date": start_date,
        "end_date": end_date,
    }

    favourite_id = save_favourite(
        user_id=current_user_id,
        query=query_text or "",
        starting_point=starting_point or "",
        context_params=context_params,
        recommendation=recommendation,
    )

    profile_source_text = " ".join(
        text for text in [query_text, recommendation]
        if text
    )

    profile_update = extract_profile_from_query(
        query=profile_source_text,
        context_params=context_params,
    )

    update_user_profile(current_user_id, profile_update)

    return (
        f"Recommendation saved. Favourite id: {favourite_id}. "
        f"Profile updated: {profile_update}"
    )


def show_user_profile(current_user_id: Optional[int]):
    return render_profile_bars(current_user_id)


def generate_text(
    current_user_id: Optional[int],
    country: Optional[str],
    starting_point: Optional[str],
    query_text: str,
    model: Optional[str] = "gemini-2.5-flash",
    cost_preference: Optional[str] = "Normal",
    temporary_events: Optional[bool] = True,
    weather: Optional[bool] = False,
    carbon_footprint_preference: Optional[str] = "Normal Carbon",
    max_tokens: Optional[int] = 2048,
    temp: Optional[float] = 0.49,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    is_sustainable: Optional[bool] = False,
):
    model_params = {
        "max_tokens": max_tokens,
        "temperature": temp,
    }

    user_profile = None

    if current_user_id is not None:
        user_profile = get_user_profile(current_user_id)

    pipeline_response = pipeline(
        query=query_text,
        model_name=model,
        sustainability=is_sustainable,
        starting_point=starting_point,
        user_profile=user_profile,
        start_date=start_date,
        end_date=end_date,
        cost_preference=cost_preference,
        temporary_events=temporary_events,
        weather=weather,
        weather_preference="Prefer dry weather" if weather else None,
        carbon_footprint=1 if carbon_footprint_preference else 0,
        carbon_footprint_preference=carbon_footprint_preference,
        **model_params,
    )

    if pipeline_response is None:
        return "Error while generating response! Please try again."

    return pipeline_response
