from typing import Callable, Tuple, Optional

import gradio as gr

from src.ui.components.inputs import get_places, update_cities, main_component
from src.ui.templates.example_data import EXAMPLES


def load_examples(
        country: gr.components.Component,
        starting_point: gr.components.Component,
        query: gr.components.Component,
        model: gr.components.Component,
        cost_preference: gr.components.Component,
        carbon_footprint_preference: gr.components.Component,
        output: gr.components.Component,
        generate_text_fn: Callable[
            [str, Optional[str], Optional[bool], Optional[int], Optional[float], Optional[str]],
            str],
) -> gr.Examples:
    # Load the places data
    df = get_places()
    # Provide examples
    example_data = EXAMPLES
    gr.Examples(
        examples=example_data,
        inputs=[country, starting_point, query, model, cost_preference, carbon_footprint_preference],
        fn=generate_text_fn,
        outputs=[output],
        cache_examples=True,
    )

    starting_point.change(
        fn=lambda selected_country: update_cities(selected_country, df),
        inputs=country,
        outputs=starting_point
    )


def load_buttons(
        country: gr.components.Component,
        starting_point: gr.components.Component,
        query: gr.components.Component,
        model: gr.components.Component,
        cost_preference: gr.components.Component,
        carbon_footprint_preference: gr.components.Component,
        max_new_tokens: gr.components.Component,
        temperature: gr.components.Component,
        start_date: gr.components.Component,
        end_date: gr.components.Component,
        output: gr.components.Component,
        generate_text_fn: Callable[
            [Optional[str], str, Optional[str], Optional[bool], Optional[int], Optional[float]],
            str],
        clear_fn: Callable[[], None]
) -> gr.Group:
    """
    Load and return buttons for the Gradio interface.

    Args:
        query: The input component for user queries.
        model: The input component for selecting the model.
        sustainable: The input component for sustainable travel options.
        starting_point: The input component for the user's starting point.
        output: The output component for displaying the generated text.
        generate_text_fn: The function to be called on submit to generate text.
        clear_fn: The function to clear the input fields and output.

    Returns:
        Gradio Group component containing the buttons.
        :param clear_fn:
        :param generate_text_fn:
        :param country:
    """
    with gr.Group() as btns:
        with gr.Row():
            submit_btn = gr.Button("Search", variant="primary")
            clear_btn = gr.Button("Clear", variant="secondary")
            cancel_btn = gr.Button("Cancel", variant="stop")

        # Bind actions to the buttons
        submit_btn.click(
            fn=generate_text_fn,  # Function to generate text
            inputs=[
                country,
                starting_point,
                query,
                model,
                cost_preference,
                carbon_footprint_preference,
                max_new_tokens,
                temperature,
                start_date,
                end_date,
            ],  # Input components for generation
            outputs=[output]  # Output component
        )
        clear_btn.click(
            fn=clear_fn,  # Function to clear inputs
            inputs=[query, model, starting_point, country, cost_preference, carbon_footprint_preference, output],  # inputs for clearing
            outputs=[query, model, starting_point, country, cost_preference, carbon_footprint_preference, output]  # Clear all inputs and output
        )
        cancel_btn.click(
            fn=clear_fn,  # Function to cancel and clear inputs
            inputs=[query, model, starting_point, country, cost_preference, carbon_footprint_preference, output],  #inputs for cancel
            outputs=[query, model, starting_point, country, cost_preference, carbon_footprint_preference, output]  # Clear all inputs and output
        )
    return btns


def model_settings() -> Tuple[gr.Slider, gr.Slider]:
    """
    Creates the model settings components and returns them.

    Returns:
        Tuple containing:
        - max_new_tokens: Slider for setting the maximum number of new tokens.
        - temperature: Slider for setting the temperature.
    """
    with gr.Accordion("Settings", open=False):
        # Slider for maximum number of new tokens
        max_new_tokens = gr.Slider(
            label="Max new tokens",
            value=1024,
            minimum=0,
            maximum=8192,
            step=64,
            interactive=True,
            visible=True,
            info="The maximum number of output tokens"
        )

        # Slider for temperature
        temperature = gr.Slider(
            label="Temperature",
            step=0.01,
            minimum=0.01,
            maximum=1.0,
            value=0.49,
            interactive=True,
            visible=True,
            info="The value used to modulate the logits distribution"
        )

    return max_new_tokens, temperature
