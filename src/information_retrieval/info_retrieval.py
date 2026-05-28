import sys
import re
import os
import json

from src.vectordb.ingest import create_wikivoyage_docs_db_and_add_data, create_wikivoyage_listings_db_and_add_data
from src.helpers.living_cost_loader import get_cost_scores
from src.helpers.carbon_footsprint_loader import calculate_emissions
from src.helpers.event_loader import get_events_for_cities
from src.weather import get_rain_summary

sys.path.append("../")
from src.vectordb.search import search_wikivoyage_listings, search_wikivoyage_docs
from src.sustainability import s_fairness
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

from src.helpers.data_loaders import load_scores


def get_travel_months(query):
    """

    Function to parse the user's query and search if month of travel has been provided by the user.

    Args:
    - query: str

    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    seasons = {
        "spring": ["March", "April", "May"],
        "summer": ["June", "July", "August"],
        "fall": ["September", "October", "November"],
        "autumn": ["September", "October", "November"],
        "winter": ["December", "January", "February"]
    }

    months_in_query = []

    for month in months:
        if re.search(r'\b' + month + r'\b', query, re.IGNORECASE):
            months_in_query.append(month)

    # Check for seasons in the query
    for season, season_months in seasons.items():
        if re.search(r'\b' + season + r'\b', query, re.IGNORECASE):
            months_in_query += season_months

    # Return None if neither months nor seasons are found
    return months_in_query


def resolve_starting_coord(starting_point):
    """
    Resolve starting_point to a (latitude, longitude) tuple.

    Accepted formats:
    - dict with keys 'latitude'/'longitude' or 'lat'/'lng'
    - tuple/list (lat, lng)
    - city name string (will lookup in cities_csv)
    """
    # dict
    if isinstance(starting_point, dict):
        lat = starting_point.get("latitude") or starting_point.get("lat")
        lng = starting_point.get("longitude") or starting_point.get("lng")
        if lat is not None and lng is not None:
            return (float(lat), float(lng))

    # tuple or list
    if isinstance(starting_point, (list, tuple)) and len(starting_point) >= 2:
        try:
            return (float(starting_point[0]), float(starting_point[1]))
        except Exception:
            pass

    # string -> city name lookup
    if isinstance(starting_point, str):
        try:
            import pandas as pd
            from src.data_directories import cities_csv
            df = pd.read_csv(cities_csv)
            match = df[df['city'].str.lower() == starting_point.lower()]
            if not match.empty and 'lat' in match.columns and 'lng' in match.columns:
                return (float(match.iloc[0]['lat']), float(match.iloc[0]['lng']))
        except Exception:
            pass

    raise ValueError('Cannot resolve starting_point to (latitude, longitude)')


def get_wikivoyage_context(query, limit=10, reranking=0):
    """

    Function to retrieve the relevant documents and listings from the wikivoyage database. Works in two steps:
    (i) the relevant cities are returned by the wikivoyage_docs table and (ii) then passed on to the wikivoyage listings database to retrieve further information.
    The user can pass a limit of how many results the search should return as well as whether to perform reranking (uses a CrossEncoderReranker)

    Args:
        - query: str
        - limit: int
        - reranking: bool

    """

    # limit = params['limit']
    # reranking = params['reranking']

    docs = search_wikivoyage_docs(query, limit, reranking)
    logger.info("Finished getting chunked wikivoyage docs.")

    results = {}
    for doc in docs:
        results[doc['city']] = {key: value for key, value in doc.items() if key != 'city'}
        # add short aliases for coordinates for easier access elsewhere
        if 'latitude' in results[doc['city']] and 'longitude' in results[doc['city']]:
            results[doc['city']]['lat'] = results[doc['city']]['latitude']
            results[doc['city']]['lng'] = results[doc['city']]['longitude']
        results[doc['city']]['listings'] = []

    cities = [result['city'] for result in docs]

    listings = search_wikivoyage_listings(query, cities, limit, reranking)
    logger.info("Finished getting wikivoyage listings.")
    # logger.info(type(docs), type(listings))

    for listing in listings:
        # logger.info(listing['city'])
        results[listing['city']]['listings'].append({
            'type': listing['type'],
            'name': listing['title'],
            'description': listing['description']
        })

    logger.info("Returning retrieval results.")
    return results


def get_sustainability_scores(starting_point: str, query: str, destinations: list):
    """

    Function to get the s-fairness scores for each destination for the given month (or the ideal month of travel if the user hasn't provided a month).
    If multiple months are provided (or season), then the month with the minimum s-fairness score is chosen for the city.

    Args:
        - query: str
        - destinations: list

    """

    result = []  # list of dicts of the format {city: <city>, month: <month>, }
    city_scores = {}

    months = get_travel_months(query)
    logger.info("Finished parsing query for months.")

    popularity_data = load_scores("popularity")
    seasonality_data = load_scores("seasonality")
    emissions_data = load_scores("emissions")
    data = [popularity_data, seasonality_data, emissions_data]

    for city in destinations:
        if city not in city_scores:
            city_scores[city] = []

        if not months:  # no month(s) or seasons provided by the user
            city_scores[city].append(s_fairness.compute_sfairness_score(data, starting_point, city))
        else:
            for month in months:
                city_scores[city].append(s_fairness.compute_sfairness_score(data, starting_point, city, month))

    logger.info("Finished getting s-fairness scores.")

    for city, scores in city_scores.items():

        no_result = 0
        for score in scores:
            if not score['month']:
                no_result = 1
                result.append({
                    'city': city,
                    'month': 'No data available',
                    's-fairness': 'No data available',
                    'mode': 'No data available'
                })
                break

        if not no_result:
            min_score = min(scores, key=lambda x: x['s-fairness'])
            result.append({
                'city': city,
                'month': min_score['month'],
                's-fairness': min_score['s-fairness'],
                'mode': min_score['mode'],
            })

    logger.info("Returning s-fairness results.")
    return result


def get_cities(context: dict):
    """
    Only to be used for testing! Function that returns a list of cities with their s-fairness scores, provided the retrieved context

    Args:
        - context: dict

    """

    recommended_cities = []
    info = context[list(context.keys())[0]]
    for city, info in context.items():
        city_info = {
            'city': city,
            'country': info['country']
        }

        if "sustainability" in info:
            city_info['month'] = info['sustainability']['month']
            city_info['s-fairness'] = info['sustainability']['s-fairness']

        recommended_cities.append(city_info)

    if "sustainability" in info:
        def get_s_fairness_value(item):
            s_fairness = item['s-fairness']
            if s_fairness == 'No data available':
                return float('inf')  # Assign a high value for "No data available"
            return s_fairness

        # Sort the list using the custom key
        sorted_cities = sorted(recommended_cities, key=get_s_fairness_value)
        return sorted_cities

    else:
        return recommended_cities


def get_context(starting_point: str, query: str, **params):
    """
    Function that returns all the context: from the database, as well as the respective s-fairness scores for the
    destinations. The default does not consider S-Fairness scores, i.e. to append sustainability scores, a non-zero
    parameter "sustainability" needs to be explicitly passed to params.

    Args:
        - query: str
        - params: dict; contains value of the limit and reranking (and sustainability)

    """

    limit = 3
    reranking = 1

    if 'limit' in params:
        limit = params['limit']

    if 'reranking' in params:
        reranking = params['reranking']

    wikivoyage_context = get_wikivoyage_context(query, limit, reranking)
    recommended_cities = wikivoyage_context.keys()
    # resolve starting point into (latitude, longitude)
    starting_coord = None
    try:
        starting_coord = resolve_starting_coord(starting_point)
    except Exception as e:
        logger.warning(f"Could not resolve starting_point to coordinates: {e}")

    if 'sustainability' in params and params['sustainability']:
        s_fairness_scores = get_sustainability_scores(starting_point, query, recommended_cities)

        for score in s_fairness_scores:
            wikivoyage_context[score['city']]['sustainability'] = {
                'month': score['month'],
                's-fairness': score['s-fairness'],
                'transport': score['mode']
            }
            
    
    if "cost_of_living" in params and params["cost_of_living"]:
        cost_scores = get_cost_scores(recommended_cities)

        cost_by_city = {
            item["city"]: item
            for item in cost_scores
        }

        for city in recommended_cities:
            if city in cost_by_city:
                item = cost_by_city[city]
                wikivoyage_context[city]["cost_of_living"] = {
                    "monthly_living_cost_usd": item["monthly_living_cost_usd"],
                    "cost_index": item["cost_index"],
                    "cost_salary_ratio": item["cost_salary_ratio"],
                    "breakdown": item["breakdown"],
                    "data_quality": item["data_quality"],
                }
            else:
                wikivoyage_context[city]["cost_of_living"] = {
                    "monthly_living_cost_usd": "No data available",
                    "cost_index": "No data available",
                    "cost_salary_ratio": "No data available",
                    "breakdown": {},
                    "data_quality": "No data available",
                }
    if "carbon_footprint" in params and params["carbon_footprint"]:
        for city in recommended_cities:
            # wikivoyage_context stores per-city info (including latitude/longitude)
            city_info = wikivoyage_context.get(city, {})
            lat = city_info.get('latitude')
            lng = city_info.get('longitude')
            if lat is None:
                lat = city_info.get('lat')
            if lng is None:
                lng = city_info.get('lng')
            print("DEBUG city =", city)
            print("DEBUG city_info keys =", city_info.keys())
            print("DEBUG destination lat/lng =", lat, lng)

            destination_coord = None
            if lat is not None and lng is not None:
                try:
                    destination_coord = (float(lat), float(lng))
                except (TypeError, ValueError):
                    destination_coord = None

            if destination_coord is None:
                try:
                    destination_coord = resolve_starting_coord(city)
                    print("DEBUG destination coord loaded from CSV =", destination_coord)
                except Exception as e:
                    print("DEBUG destination coord lookup failed =", city, e)

            if starting_coord and destination_coord:
                carbon = calculate_emissions(starting_coord, destination_coord)
                print("DEBUG carbon =", carbon)
                wikivoyage_context[city]["carbon_footprint"] = carbon
            else:
                print("DEBUG carbon skipped for", city)
                wikivoyage_context[city]["carbon_footprint"] = {
                    "distance_km": "No data available",
                    "inferred_mode": "No data available",
                    "estimated_co2_kg": "No data available",
                    "carbon_category": "No data available",
                }
    if params.get("weather"):
        for city in recommended_cities:
            city_info = wikivoyage_context.get(city, {})

            lat = city_info.get("latitude") or city_info.get("lat")
            lng = city_info.get("longitude") or city_info.get("lng")

            destination_coord = None

            if lat is not None and lng is not None:
                try:
                    destination_coord = (float(lat), float(lng))
                except (TypeError, ValueError):
                    destination_coord = None

            if destination_coord is None:
                try:
                    destination_coord = resolve_starting_coord(city)
                except Exception:
                    destination_coord = None

            if destination_coord:
                weather = get_rain_summary(
                    lat=destination_coord[0],
                    lon=destination_coord[1],
                    start_date=params.get("start_date"),
                    end_date=params.get("end_date"),
                )
            else:
                weather = {
                    "available": False,
                    "rain_risk": "unknown",
                    "reason": "No coordinates available",
                    "daily": [],
                }

            wikivoyage_context[city]["weather"] = weather
    if params.get("temporary_events"):
        event_results = get_events_for_cities(
            cities=recommended_cities,
            query=query,
            start_date=params.get("start_date"),
            end_date=params.get("end_date"),
            size_per_city=params.get("events_per_city", 3),
        )

        for city in recommended_cities:
            wikivoyage_context[city]["temporary_events"] = event_results.get(city, [])
  
    return wikivoyage_context


def test():
    queries = []
    query = "Suggest some places to visit during winter. I like hiking, nature and the mountains and I enjoy skiing " \
            "in winter. "
    starting_point = "Munich"
    context = None

    try:
        context = get_context(starting_point, query, sustainability=1)
        # cities = get_cities(context)
        # print(cities)
    except FileNotFoundError as e:
        try:
            create_wikivoyage_docs_db_and_add_data()
            create_wikivoyage_listings_db_and_add_data()

            try:
                context = get_context(starting_point, query, sustainability=1)
                # cities = get_cities(context)
                # print(cities)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(f"Error while getting context: {e}, {(exc_type, fname, exc_tb.tb_lineno)}")

        except Exception as e:
            logger.error(f"Error while creating DB: {e}")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(f"Error while getting context: {e}, {(exc_type, fname, exc_tb.tb_lineno)}")

    file_path = os.path.join(os.getcwd(), "test_results", "test_result.json")
    with open(file_path, 'w') as file:
        json.dump(context, file)

    return context

def test2():
    query = (
        "Suggest some places to visit during winter. "
        "I like hiking, nature and the mountains and I enjoy skiing in winter."
    )
    starting_point = "Munich"

    context_params = {
        'limit': 5,
        'reranking': 0,
        'sustainability': 0,
        'cost_of_living':1,
        'carbon_footprint': 1,
        "temporary_events": 1,
        "events_per_city": 3,
        "weather": 1,
    }

    context = None

    try:
        context = get_context(
            starting_point=starting_point,
            query=query,
            **context_params
        )

    except FileNotFoundError as e:
        logger.warning(f"Database not found, trying to create it first: {e}")

        try:
            create_wikivoyage_docs_db_and_add_data()
            create_wikivoyage_listings_db_and_add_data()

            context = get_context(
                starting_point=starting_point,
                query=query,
                **context_params
            )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(
                f"Error after creating DB: {e}, "
                f"{(exc_type, fname, exc_tb.tb_lineno)}"
            )
            context = {
                "error": str(e),
                "stage": "after_db_creation",
            }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(
            f"Error while getting context: {e}, "
            f"{(exc_type, fname, exc_tb.tb_lineno)}"
        )
        context = {
            "error": str(e),
            "stage": "get_context",
        }

    output_dir = os.path.join(os.getcwd(), "test_results")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, "test_result.json")

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(context, file, ensure_ascii=False, indent=2)

    logger.info(f"Saved test result to {file_path}")

    return context

if __name__ == "__main__":
    context = test2()

    print(context)
