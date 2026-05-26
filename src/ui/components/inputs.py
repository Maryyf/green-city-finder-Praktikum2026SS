from typing import Tuple, Optional, Any

import gradio as gr

from src.helpers.data_loaders import load_places
from src.text_generation.mapper import MODEL_MAPPER


def get_places():
    #data_file = "cities/eu_200_cities.csv"
    data_file = "city_abstracts_embeddings.csv"
    df = load_places(data_file)
    df = df.sort_values(by=['country', 'city'])
    return df


def update_cities(selected_country, df):
    if not selected_country:
        return gr.update(choices=[], value=None, interactive=False)
    # Filter cities based on the selected country
    filtered_cities = df[df['country'] == selected_country]['city'].tolist()
    return gr.Dropdown(choices=filtered_cities, interactive=True)


def main_component() -> Tuple[gr.Dropdown, gr.Dropdown, gr.Textbox, gr.Dropdown, gr.Dropdown, gr.Checkbox, gr.Dropdown, Any, Any]:
    """
    Creates the main Gradio interface components and returns them.

    Returns:
        Tuple containing:
        - countries: Dropdown for selecting the country.
        - starting_point: Dropdown for selecting the starting point.
        - query: Textbox for entering the user query.
        - model: Dropdown for selecting the model.
        - start_date: Optional start date for travel (gr.Date).
        - end_date: Optional end date for travel (gr.Date).
    """
    df = get_places()
    country_names = list(df.country.unique())
    cities = list(df.city.unique())
    with gr.Group():
        # Country selection dropdown
        country = gr.Dropdown(choices=country_names, multiselect=False, label="Country")

        # Starting point selection dropdown
        starting_point = gr.Dropdown(choices=cities, multiselect=False,
                                     label="City",
                                     info="Select a city as your starting point.")

        # # When a country is selected, update the starting point options
        country.select(
            fn=lambda selected_country: update_cities(selected_country, df),
            inputs=country,
            outputs=starting_point
        )

        # User query input
        query = gr.Textbox(label="Enter your preferences e.g. beaches, night life etc. and ask for your "
                                 "recommendation for European cities!", placeholder="Ask for your city recommendation"
                                                                                    " here!")
        # Cost preference dropdown
        cost_preference = gr.Dropdown(
            choices=["Luxurious", "Normal", "Cheap"],
            value="Normal",
            multiselect=False,
            label="Cost preference",
            info="Choose your preferred travel budget level."
        )
        temporary_events = gr.Checkbox(
            label="Include temporary events",
            value=True,
            info="Use Ticketmaster to include live events during your travel dates."
        )
        # Carbon footprint preference dropdown
        carbon_footprint_preference = gr.Dropdown(
            choices=["Extremely Low Carbon", "Normal Carbon", "High Carbon"],
            value="Normal Carbon",
            multiselect=False,
            label="Carbon footprint preference",
            info="Choose your preferred level of carbon footprint in your travel plans."
        )

        # Optional date inputs for travel (use Textbox for compatibility across Gradio versions)
        start_date = gr.Textbox(label="Start date (optional)", placeholder="YYYY-MM-DD")
        end_date = gr.Textbox(label="End date (optional)", placeholder="YYYY-MM-DD")

        # Checkbox for sustainable travel option
        # sustainable = gr.Checkbox(
        #     label="Sustainable",
        #     info="Do you want your recommendations to be sustainable with regards to the environment, "
        #          "your starting location, and month of travel?"
        # )

        models = list(MODEL_MAPPER.keys())[:2]
        # Model selection dropdown
        model = gr.Dropdown(
            choices=models,
            label="Model",
            value="gemini-2.5-flash",
            info="Select your model. The model will generate sustainable recommendations based on your query."
        )

    # Return all the components individually (including optional dates)
    return country, starting_point, query, model, cost_preference, temporary_events, carbon_footprint_preference, start_date, end_date
