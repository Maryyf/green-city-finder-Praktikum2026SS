import os
import logging
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.INFO)

TICKETMASTER_EVENTS_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


def _to_ticketmaster_datetime(date_str: Optional[str], end_of_day: bool = False) -> Optional[str]:
    """
    Convert YYYY-MM-DD to Ticketmaster ISO 8601 datetime.
    """
    if not date_str:
        return None

    if end_of_day:
        return f"{date_str}T23:59:59Z"

    return f"{date_str}T00:00:00Z"


def infer_event_classification(query: str) -> Optional[str]:
    """
    Infer a rough Ticketmaster classification from the user's query.

    This is intentionally simple. If unsure, return None so the API
    does not over-filter useful events.
    """
    query_lower = query.lower()

    if any(word in query_lower for word in ["music", "concert", "festival", "nightlife", "club", "party"]):
        return "music"

    if any(word in query_lower for word in ["football", "soccer", "basketball", "tennis", "sport", "sports"]):
        return "sports"

    if any(word in query_lower for word in ["theatre", "theater", "opera", "musical", "performance", "arts"]):
        return "arts & theatre"

    if any(word in query_lower for word in ["family", "kids", "children"]):
        return "family"

    return None


def search_events_for_city(
    city: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    country_code: Optional[str] = None,
    keyword: Optional[str] = None,
    classification_name: Optional[str] = None,
    size: int = 3,
) -> list[dict]:
    """
    Search Ticketmaster temporary events for one city.

    Returns simplified event data suitable for adding into RAG context.
    """
    api_key = os.getenv("TICKETMASTER_API_KEY")

    if not api_key:
        logger.warning("TICKETMASTER_API_KEY is not set. Skipping Ticketmaster events.")
        return []

    params = {
        "apikey": api_key,
        "city": city,
        "size": size,
        "sort": "date,asc",
    }

    start_datetime = _to_ticketmaster_datetime(start_date)
    end_datetime = _to_ticketmaster_datetime(end_date, end_of_day=True)

    if start_datetime:
        params["startDateTime"] = start_datetime

    if end_datetime:
        params["endDateTime"] = end_datetime

    if country_code:
        params["countryCode"] = country_code

    if keyword:
        params["keyword"] = keyword

    if classification_name:
        params["classificationName"] = classification_name

    try:
        response = requests.get(
            TICKETMASTER_EVENTS_URL,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        logger.warning("Ticketmaster request failed for %s: %s", city, e)
        return []

    raw_events = data.get("_embedded", {}).get("events", [])

    events = []

    for event in raw_events:
        start = event.get("dates", {}).get("start", {})

        venue_name = None
        venue_city = None
        venue_country = None

        venues = event.get("_embedded", {}).get("venues", [])
        if venues:
            venue = venues[0]
            venue_name = venue.get("name")
            venue_city = venue.get("city", {}).get("name")
            venue_country = venue.get("country", {}).get("name")

        segment = None
        genre = None

        classifications = event.get("classifications", [])
        if classifications:
            classification = classifications[0]
            segment = classification.get("segment", {}).get("name")
            genre = classification.get("genre", {}).get("name")

        events.append({
            "name": event.get("name"),
            "date": start.get("localDate"),
            "time": start.get("localTime"),
            "venue": venue_name,
            "venue_city": venue_city,
            "venue_country": venue_country,
            "segment": segment,
            "genre": genre,
            "url": event.get("url"),
        })

    return events


def get_events_for_cities(
    cities: list[str],
    query: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    size_per_city: int = 3,
) -> dict[str, list[dict]]:
    """
    Fetch events for multiple candidate cities.
    """
    classification_name = infer_event_classification(query)

    results = {}

    for city in cities:
        events = search_events_for_city(
            city=city,
            start_date=start_date,
            end_date=end_date,
            classification_name=classification_name,
            size=size_per_city,
        )

        results[city] = events

    return results


if __name__ == "__main__":
    test_events = search_events_for_city(
        city="Vienna",
        start_date="2026-07-01",
        end_date="2026-07-07",
        size=5,
    )

    for item in test_events:
        print(item)