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

    max_score = max(numeric_profile.values()) if numeric_profile else 0

    if max_score <= 0:
        return f"""
        {_travel_preference_title()}
        <div class="profile-empty-state">
            Your profile is empty. Save recommendations to build personalised preference bars.
        </div>
        """

    rows = []

    for field in PROFILE_FIELDS:
        score = numeric_profile[field]
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
