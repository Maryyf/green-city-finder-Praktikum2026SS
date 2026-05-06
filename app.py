import gradio as gr
import sys
from src.ui.components.form import form_block
from src.ui.setup import load_html_from_file
from src.text_generation.vertexai_setup import initialize_vertexai_params

sys.path.append("./src")


def create_ui():
    initialize_vertexai_params()
    # Path to HTML file
    html_file_path = 'src/ui/templates/intro.html'

    # Create the Gradio HTML component
    html_content = load_html_from_file(html_file_path)

    with gr.Blocks(
            theme=gr.themes.Default(primary_hue=gr.themes.colors.green, secondary_hue=gr.themes.colors.blue)) as app:
        gr.HTML(html_content)
        form_block()

    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch()
