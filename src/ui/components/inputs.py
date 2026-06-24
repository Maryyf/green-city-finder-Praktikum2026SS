import gradio as gr

from src.helpers.data_loaders import load_places
from src.text_generation.mapper import MODEL_MAPPER


def get_places():
    df = load_places("city_abstracts_embeddings.csv")
    return df.sort_values(by=["country", "city"])


def update_cities(selected_country, df):
    if not selected_country:
        return gr.update(choices=[], value=None, interactive=False)

    cities = df[df["country"] == selected_country]["city"].tolist()
    return gr.update(choices=cities, value=None, interactive=True)


def main_component():
    """Build the compact search and filter controls."""
    df = get_places()
    country_names = list(df.country.unique())
    cities = list(df.city.unique())

    with gr.Column(elem_classes=["filter-stack"]):
        query = gr.Textbox(
            label="Trip preferences",
            placeholder="Museums, hiking, beaches, nightlife...",
            lines=4,
        )

        with gr.Row(elem_classes=["location-row"]):
            country = gr.Dropdown(
                choices=country_names,
                multiselect=False,
                label="Country",
            )
            starting_point = gr.Dropdown(
                choices=cities,
                multiselect=False,
                label="Starting city",
            )

        with gr.Row(elem_classes=["date-row"]):
            start_date = gr.Textbox(
                label="Start date",
                placeholder="YYYY-MM-DD",
            )
            end_date = gr.Textbox(
                label="End date",
                placeholder="YYYY-MM-DD",
            )

        with gr.Accordion("Trip filters", open=False, elem_classes=["filter-accordion"]):
            with gr.Row():
                cost_preference = gr.Dropdown(
                    choices=["Luxurious", "Normal", "Cheap"],
                    value="Normal",
                    multiselect=False,
                    label="Budget",
                )
                carbon_footprint_preference = gr.Dropdown(
                    choices=[
                        "Extremely Low Carbon",
                        "Normal Carbon",
                        "High Carbon",
                    ],
                    value="Normal Carbon",
                    multiselect=False,
                    label="Carbon preference",
                )

            with gr.Row(elem_classes=["toggle-row"]):
                weather = gr.Checkbox(
                    label="Prefer dry weather",
                    value=False,
                )
                temporary_events = gr.Checkbox(
                    label="Include temporary events",
                    value=True,
                )

        with gr.Accordion("Model", open=False, elem_classes=["model-accordion"]):
            models = list(MODEL_MAPPER.keys())[:2]
            model = gr.Dropdown(
                choices=models,
                label="Generation model",
                value="gemini-2.5-flash",
            )

    country.change(
        fn=lambda selected_country: update_cities(selected_country, df),
        inputs=country,
        outputs=starting_point,
    )

    return (
        country,
        starting_point,
        query,
        model,
        cost_preference,
        temporary_events,
        weather,
        carbon_footprint_preference,
        start_date,
        end_date,
    )
