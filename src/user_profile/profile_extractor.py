PROFILE_KEYWORDS = {
    "beach": [
        "beach", "beaches", "sea", "seaside", "coast", "coastal",
        "island", "islands", "swimming", "sunbathing"
    ],
    "nature": [
        "nature", "natural", "lake", "lakes", "mountain", "mountains",
        "forest", "forests", "river", "rivers", "landscape", "scenery"
    ],
    "outdoor": [
        "outdoor", "hiking", "cycling", "skiing", "walking",
        "trekking", "climbing", "camping"
    ],
    "historic": [
        "history", "historic", "historical", "castle", "castles",
        "old town", "ancient", "heritage", "monument", "monuments"
    ],
    "culture": [
        "culture", "cultural", "art", "arts", "gallery", "galleries",
        "architecture", "museum", "museums", "theatre", "theater", "opera"
    ],
    "nightlife": [
        "nightlife", "club", "clubs", "bar", "bars", "party", "parties",
        "concert", "concerts", "festival", "festivals", "music"
    ],
    "food": [
        "food", "restaurant", "restaurants", "cafe", "cafes",
        "wine", "beer", "local cuisine", "cuisine", "dining"
    ],
    "shopping": [
        "shopping", "shop", "shops", "market", "markets",
        "fashion", "boutique", "mall", "malls"
    ],
}


def _contains_keyword(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in keywords)


def extract_profile_from_query(query: str, context_params: dict | None = None) -> dict:
    context_params = context_params or {}
    query = query or ""

    profile_update = {}

    for field, keywords in PROFILE_KEYWORDS.items():
        if _contains_keyword(query, keywords):
            profile_update[field] = 1

    cost_preference = context_params.get("cost_preference")
    if cost_preference == "Cheap":
        profile_update["low_cost"] = 1

    carbon_preference = context_params.get("carbon_footprint_preference")
    if carbon_preference == "Extremely Low Carbon":
        profile_update["low_carbon"] = 1

    weather = context_params.get("weather")
    weather_preference = context_params.get("weather_preference")
    if weather or weather_preference == "Prefer dry weather":
        profile_update["dry_weather"] = 1

    return profile_update