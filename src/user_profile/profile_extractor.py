import re


PROFILE_KEYWORDS = {
    "beach_coast": [
        "beach", "beaches", "seaside", "coast", "coastal", "island",
        "islands", "sunbathing",
    ],
    "mountains_hiking": [
        "mountain", "mountains", "hiking", "trekking", "climbing",
        "trail", "trails", "canyon",
    ],
    "nature_wildlife": [
        "nature", "natural", "forest", "forests", "lake", "lakes",
        "river", "rivers", "wildlife", "national park", "landscape",
        "scenery",
    ],
    "winter_sports": [
        "ski", "skiing", "snowboard", "snowboarding", "snowshoeing",
        "winter sports",
    ],
    "water_sports": [
        "swimming", "surfing", "diving", "snorkeling", "snorkelling",
        "kayaking", "canoeing", "sailing", "water sports",
    ],
    "history_heritage": [
        "history", "historic", "historical", "heritage", "castle",
        "castles", "ancient", "old town", "archaeology", "ruins",
        "monument", "monuments",
    ],
    "arts_museums": [
        "art", "arts", "museum", "museums", "gallery", "galleries",
        "exhibition", "exhibitions",
    ],
    "architecture": [
        "architecture", "architectural", "cathedral", "cathedrals",
        "church", "churches", "modernist", "historic buildings",
    ],
    "local_culture": [
        "culture", "cultural", "tradition", "traditions", "folklore",
        "local life", "local community", "authentic experience",
    ],
    "food_drink": [
        "food", "restaurant", "restaurants", "cafe", "cafes", "wine",
        "beer", "local cuisine", "cuisine", "dining", "gastronomy",
    ],
    "nightlife": [
        "nightlife", "night club", "night clubs", "club", "clubs",
        "bar", "bars", "party", "parties",
    ],
    "music_festivals": [
        "music", "concert", "concerts", "festival", "festivals",
        "live music", "gig", "gigs",
    ],
    "shopping_markets": [
        "shopping", "shop", "shops", "market", "markets", "fashion",
        "boutique", "boutiques", "mall", "malls",
    ],
    "wellness_relaxation": [
        "wellness", "spa", "thermal bath", "hot spring", "hot springs",
        "relax", "relaxing", "relaxation", "retreat",
    ],
    "major_city": [
        "major city", "big city", "large city", "metropolis", "urban",
        "city break", "vibrant city",
    ],
    "small_town": [
        "small town", "quiet town", "village", "villages", "countryside",
        "rural escape",
    ],
    "hidden_gems": [
        "hidden gem", "hidden gems", "off the beaten path", "offbeat",
        "less crowded", "uncrowded", "non touristy", "local secret",
    ],
    "budget": [
        "budget", "cheap", "affordable", "low cost", "inexpensive",
    ],
    "luxury": [
        "luxury", "luxurious", "premium", "five star", "high end",
    ],
    "dry_weather": [
        "dry weather", "sunny", "sunshine", "avoid rain", "low rain",
    ],
    "low_carbon": [
        "low carbon", "carbon footprint", "eco friendly", "sustainable travel",
        "avoid flights", "train travel", "low emissions",
    ],
}


def _contains_keyword(text: str, keywords: list[str]) -> bool:
    normalized_text = re.sub(r"\s+", " ", text.lower()).strip()

    return any(
        re.search(rf"\b{re.escape(keyword)}\b", normalized_text)
        for keyword in keywords
    )


def extract_profile_from_query(
    query: str,
    context_params: dict | None = None,
) -> dict:
    context_params = context_params or {}
    query = query or ""

    profile_update = {
        field: 1
        for field, keywords in PROFILE_KEYWORDS.items()
        if _contains_keyword(query, keywords)
    }

    cost_preference = context_params.get("cost_preference")
    if cost_preference == "Cheap":
        profile_update["budget"] = 1
    elif cost_preference == "Luxurious":
        profile_update["luxury"] = 1

    carbon_preference = context_params.get("carbon_footprint_preference")
    if carbon_preference == "Extremely Low Carbon":
        profile_update["low_carbon"] = 1

    weather = context_params.get("weather")
    weather_preference = context_params.get("weather_preference")
    if weather or weather_preference == "Prefer dry weather":
        profile_update["dry_weather"] = 1

    return profile_update
