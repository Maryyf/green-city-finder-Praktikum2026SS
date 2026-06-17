from typing import Optional

from src.pipeline import pipeline
from src.user_profile.db import (
    create_user,
    authenticate_user,
    get_user_profile,
    save_favourite,
    update_user_profile,
)
from src.user_profile.profile_extractor import extract_profile_from_query

# Define the clear function dynamically based on the number of inputs
def clear(*args):
    return tuple([None] * len(args))  # Return None for each input/output component dynamically

def register_user(email: str, password: str):
    try:
        user_id = create_user(email, password)
        return user_id, f"Registered and logged in as {email.strip().lower()}"
    except ValueError as e:
        return None, f"Registration failed: {e}"
    except Exception as e:
        return None, f"Registration failed: {e}"


def login_user(email: str, password: str):
    try:
        user_id = authenticate_user(email, password)

        if user_id is None:
            return None, "Login failed: invalid email or password"

        return user_id, f"Logged in as {email.strip().lower()}"

    except Exception as e:
        return None, f"Login failed: {e}"

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

    return f"Recommendation saved. Favourite id: {favourite_id}. Profile updated: {profile_update}"
    
def show_user_profile(current_user_id: Optional[int]):
    if current_user_id is None:
        return "Please log in first."

    profile = get_user_profile(current_user_id)

    if not profile:
        return "No profile found."

    active_items = {
        key: value
        for key, value in profile.items()
        if value
    }

    if not active_items:
        return "Your profile is empty. Save recommendations to build it."

    lines = [
        f"{key}: {float(value):.2f}"
        for key, value in sorted(active_items.items())
    ]

    return "\n".join(lines)

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
        'max_tokens': max_tokens,
        'temperature': temp
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
        **model_params
    )

    print("DEBUG country =", country)
    print("DEBUG starting_point =", starting_point)
    print("DEBUG query_text =", query_text)
    print("DEBUG model =", model)
    print("DEBUG max_tokens =", max_tokens)
    print("DEBUG temp =", temp)
    print("DEBUG start_date =", start_date)
    print("DEBUG end_date =", end_date)
    print("DEBUG cost_preference =", cost_preference)
    print("DEBUG temporary_events =", temporary_events)
    print("DEBUG carbon_footprint_preference =", carbon_footprint_preference)

    if pipeline_response is None:
        return "Error while generating response! Please try again."
    return pipeline_response
