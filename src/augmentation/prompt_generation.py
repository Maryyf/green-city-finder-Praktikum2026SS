from src.information_retrieval import info_retrieval as ir
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
from src.augmentation.prompts import (
    SYSTEM_PROMPT,
    SUSTAINABILITY_PROMPT,
    USER_PROMPT,
    COST_PROMPT,
    CARBON_PROMPT,
    COST_CARBON_PROMPT,
    COST_TEMPORARY_EVENTS_PROMPT,
)

def generate_prompt(query, context, template=None):
    """
    Function that generates the prompt given the user query and retrieved context. A specific prompt template will be
    used if provided, otherwise the default base_prompt template is used.

    Args: 
        - query: str
        - context: list[dict]
        - template: str
    
    """

    if template:
        SYS_PROMPT = template
    else:
        SYS_PROMPT = SYSTEM_PROMPT

    formatted_prompt = f"{USER_PROMPT.format(query, context)}"
    messages = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": formatted_prompt}
    ]

    return messages


def format_context(context):
    """
    Function that formats the retrieved context in a way that is easy for the LLM to understand. 

    Args:
        - context: list[dict]; retrieved context 
    
    """

    formatted_context = ''

    for i, (city, info) in enumerate(context.items()):

        text = f"Option {i + 1}: {city} is a city in {info['country']}."
        info_text = f"Here is some information about the city. {info['text']}"

        attractions_text = "Here are some attractions: "
        att_flag = 0
        restaurants_text = "Here are some places to eat/drink: "
        rest_flag = 0

        hotels_text = "Here are some hotels: "
        hotel_flag = 0

        if len(info['listings']):
            for listing in info['listings']:
                if listing['type'] in ['see', 'do', 'go', 'view']:
                    att_flag = 1
                    attractions_text += f"{listing['name']} ({listing['description']}), "
                elif listing['type'] in ['eat', 'drink']:
                    rest_flag = 1
                    restaurants_text += f"{listing['name']} ({listing['description']}), "
                else:
                    hotel_flag = 1
                    hotels_text += f"{listing['name']} ({listing['description']}), "

        # If we add sustainability in the end then it could get truncated because of context window
        if "sustainability" in info:
            if info['sustainability']['month'] == 'No data available':
                sfairness_text = "This city has no sustainability (or s-fairness) score available."

            else:
                sfairness_text = f"The sustainability (or s-fairness) score for {city} in {info['sustainability']['month']} is {info['sustainability']['s-fairness']}. \n "

            text += sfairness_text
        
        if "carbon_footprint" in info:
            carbon = info["carbon_footprint"]
            text += (
                f"The estimated carbon footprint from the starting point is "
                f"{carbon['estimated_co2_kg']} kg CO2e, classified as "
                f"{carbon['carbon_category']}. "
                f"The inferred transport mode is {carbon['inferred_mode']}. "
            )

        if "cost_of_living" in info:
            cost = info["cost_of_living"]

            if cost["monthly_living_cost_usd"] == "No data available":
                cost_text = f"No cost-of-living data is available for {city}. "
            else:
                cost_text = (
                    f"The estimated monthly living cost for {city} is "
                    f"{cost['monthly_living_cost_usd']} USD. "
                    f"Its relative cost index is {cost['cost_index']} out of 100, "
                    f"where lower means cheaper among the available cities. "
                )

            text += cost_text

        if "temporary_events" in info:
            events = info["temporary_events"]

            if events:
                events_text = "Temporary events during the user's travel dates: "

                for event in events[:3]:
                    event_name = event.get("name") or "Unknown event"
                    event_date = event.get("date") or "date unknown"
                    event_time = event.get("time") or ""
                    event_venue = event.get("venue") or "venue unknown"
                    segment = event.get("segment")
                    genre = event.get("genre")

                    category_parts = [
                        part for part in [segment, genre]
                        if part and part != "Undefined"
                    ]

                    category = ""
                    if category_parts:
                        category = f" ({', '.join(category_parts)})"

                    time_text = f" at {event_time}" if event_time else ""

                    events_text += (
                        f"{event_name} on {event_date}{time_text} "
                        f"at {event_venue}{category}; "
                    )

                text += "\n" + events_text

            else:
                text += "\nNo temporary events were found for this city during the user's travel dates."

        text += info_text
        
        if "weather" in info:
            weather = info["weather"]

            if weather.get("available"):
                rainy_dates = weather.get("rainy_dates", [])

                if rainy_dates:
                    rainy_dates_text = " Rain is expected on: "
                    rainy_dates_text += "; ".join(
                        f"{item['date']} ({item['precip_mm']} mm)"
                        for item in rainy_dates
     )
                    rainy_dates_text += "."
                else:
                    rainy_dates_text = " No rainy dates are expected during the travel period."
                weather_text = (
                    f"Weather during the user's travel dates: "
                    f"rain risk is {weather['rain_risk']}, with "
                    f"{weather['dry_days']} dry days and "
                    f"{weather['rainy_days']} rainy days. "
                    f"Total expected precipitation is "
                    f"{weather['total_precip_mm']} mm. "
                    f"{rainy_dates_text} "
                )
            else:
                weather_text = (
                    "Weather forecast is not available for this city "
                    f"({weather.get('reason', 'unknown reason')}). "
                )

            text +="\n" + weather_text
        

        if att_flag:
            text += f"\n{attractions_text}"

        if rest_flag:
            text += f"\n{restaurants_text}"

        if hotel_flag:
            text += f"\n{hotels_text}"

        formatted_context += text + "\n\n "

    return formatted_context


def augment_prompt(query: str, starting_point: str, context: dict, **params: dict):
    """
    Function that accepts the user query as input, obtains relevant documents and augments the prompt with the
    retrieved context, which can be passed to the LLM.

    Args: - query: str - context: retrieved context, must be formatted otherwise the LLM cannot understand the nested
    dictionaries! - sustainability: bool; if true, then the prompt is appended to instruct the LLM to use s-fairness
    scores while generating the answer - params: key-value parameters to be passed to the get_context function; sets
    the limit of results and whether to rerank the results
    
    """

    # what about the cities without s-fairness scores? i.e. they don't have seasonality data 
    updated_query = f"With {starting_point} as the starting point, {query}"
    
    user_profile = params.get("user_profile")
    profile_mode = params.get("profile_mode", "soft")
    active_profile = {}

    if user_profile:
        active_profile = {
            key: value
            for key, value in user_profile.items()
            if value
        }

    if active_profile and profile_mode == "primary":
        updated_query += (
            f" The user did not enter a new query. "
            f"Use the user's long-term travel profile as the main source of preferences: {active_profile}. "
            "Recommend destinations that best match this profile."
        )
    elif active_profile:
        updated_query += (
            f" The user's long-term travel profile is {active_profile}. "
            "Use this profile only as a soft preference. "
            "The current query is more important than the long-term profile."
        )
    prompt_with_sustainability = SUSTAINABILITY_PROMPT
    prompt_with_cost_of_living = COST_PROMPT
    prompt_with_carbon = CARBON_PROMPT
    prompt_with_cost_carbon = COST_CARBON_PROMPT
    prompt_with_cost_temporary_events = COST_TEMPORARY_EVENTS_PROMPT

    cost_preference = params.get("params", {}).get("cost_preference", "Normal")
    weather_preference = params.get("params", {}).get("weather_preference")

    # print("DEBUG augment_prompt params =", params)
    # print("DEBUG augment_prompt cost_preference =", cost_preference)

    if cost_preference == 'Cheap':
        updated_query += " My cost preference is cheap. When recommending cities, please prioritize more affordable options based on the cost-of-living data provided, while still considering sustainability and relevance to my preferences."
    elif cost_preference == 'Luxurious':
        updated_query += " My cost preference is luxurious. When recommending cities, please prioritize more luxurious options based on the cost-of-living data provided, while still considering sustainability and relevance to my preferences."
    else:
        updated_query += " My cost preference is normal. When recommending cities, please consider affordability based on the cost-of-living data provided, while still balancing sustainability and relevance to my preferences without a strong bias towards either more affordable or more luxurious options."
    
    carbon_preference = params.get("params", {}).get("carbon_footprint_preference", "Normal Carbon")
    if carbon_preference:
        updated_query += (
        f" My carbon footprint preference is {carbon_preference}. "
        "When recommending cities, first consider my cost preference, then refine the recommendations based on this carbon-footprint preference."
    )
    if weather_preference:
        updated_query += (
            f" My weather preference is {weather_preference}. "
           "If I prefer dry weather, prioritize cities with lower rain risk when the context provides weather data. If rainy dates are available, mention the specific rainy dates in the final answer."
        )
    # format context
    formatted_context = format_context(context)
    
    use_weather = params["params"].get("weather")
    use_cost = params["params"].get("cost_of_living")
    use_carbon = params["params"].get("carbon_footprint")
    use_sustainability = params["params"].get("sustainability")
    use_temporary_events = params["params"].get("temporary_events")

    if use_cost and use_temporary_events:
        prompt = generate_prompt(updated_query, formatted_context, prompt_with_cost_temporary_events)
    if use_cost and use_carbon:
        prompt = generate_prompt(updated_query, formatted_context, prompt_with_cost_carbon)
    elif use_sustainability:
        prompt = generate_prompt(updated_query, formatted_context, prompt_with_sustainability)
    elif use_cost:
        prompt = generate_prompt(updated_query, formatted_context, prompt_with_cost_of_living)
    elif use_carbon:
        prompt = generate_prompt(updated_query, formatted_context, prompt_with_carbon)
    else:
        prompt = generate_prompt(updated_query, formatted_context)

    return prompt


def test():
    context_params = {
        'limit': 3,
        'reranking': 0, 
        'sustainability': 0,
        'cost_of_living': 1,
        'carbon_footprint': 1,
        'temporary_events': 1,
        'events_per_city': 3,
        'weather': 1,
    }

    query = "Suggest some places to visit during winter. I like hiking, nature and the mountains and I enjoy skiing " \
            "in winter. "

    # without sustainability
    context = ir.get_context('Munich', query, **context_params)

    without_sfairness = augment_prompt(
        query=query,
        starting_point='Munich',
        context=context,
        params=context_params
    )
    '''
    # with sustainability
    context_params.update({'sustainability': 1})
    s_context = ir.get_context(query, **context_params)
    # s_formatted_context = format_context(s_context)

    with_sfairness = augment_prompt(
        query=query,
        context=s_context,
        params=context_params
    )
    '''
    return without_sfairness

if __name__ == "__main__":
    prompt = test()
    print(prompt)
