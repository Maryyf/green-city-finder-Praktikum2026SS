import gradio as gr

from src.ui.components.actions import generate_text, clear
from src.ui.components.inputs import main_component
from src.ui.components.static import model_settings, load_buttons, load_examples


def form_block():
    country, starting_point, query, model, cost_preference, start_date, end_date = main_component()
    output = gr.Textbox(label="Your recommendations are sustainable with respect to the environment, your starting "
                              "location, and month of travel.", lines=4)
    max_new_tokens, temperature = model_settings()

    # Load the buttons for the interface
    load_buttons(country, starting_point, query, model, cost_preference,
                 max_new_tokens, temperature,
                 start_date, end_date,
                 output,
                 generate_text_fn=generate_text,
                 clear_fn=clear)
    load_examples(country, starting_point, query, model, cost_preference, output, generate_text)
