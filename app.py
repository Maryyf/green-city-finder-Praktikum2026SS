import gradio as gr
import sys

from src.ui.components.form import form_block
from src.ui.setup import load_html_from_file
from src.ui.styles import APP_CSS
from src.text_generation.vertexai_setup import initialize_vertexai_params

sys.path.append("./src")


def create_ui():
    initialize_vertexai_params()

    html_file_path = "src/ui/templates/intro.html"
    html_content = load_html_from_file(html_file_path)

    theme = gr.themes.Default(
        primary_hue=gr.themes.colors.green,
        secondary_hue=gr.themes.colors.blue,
    )

    with gr.Blocks(
        theme=theme,
        css=APP_CSS,
        title="Green City Finder",
    ) as app:
        form_block(
            intro_html=html_content,
            app=app,
        )

    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch()
