import gradio as gr

from src.ui.components.actions import (
    generate_text,
    clear,
    register_user,
    login_user,
    save_recommendation,
    show_user_profile,
)
from src.ui.components.inputs import main_component
from src.ui.components.static import model_settings, load_buttons


def form_block():
    current_user_id = gr.State(None)

    with gr.Group():
        gr.Markdown("### Login")

        email = gr.Textbox(
            label="Email",
            placeholder="Enter your email"
        )

        password = gr.Textbox(
            label="Password",
            type="password",
            placeholder="Enter your password"
        )

        login_status = gr.Textbox(
            label="Login status",
            interactive=False
        )

        with gr.Row():
            register_btn = gr.Button("Register")
            login_btn = gr.Button("Login")

    register_btn.click(
        fn=register_user,
        inputs=[email, password],
        outputs=[current_user_id, login_status],
    )

    login_btn.click(
        fn=login_user,
        inputs=[email, password],
        outputs=[current_user_id, login_status],
    )

    country, starting_point, query, model, cost_preference, temporary_events, weather, carbon_footprint_preference, start_date, end_date = main_component()

    output = gr.Textbox(
        label="Your recommendations are sustainable with respect to the environment, your starting location, and month of travel.",
        lines=4
    )
    
    save_status = gr.Textbox(
        label="Save status",
        interactive=False
    )
    
    profile_output = gr.Textbox(
        label="User profile",
        lines=8,
        interactive=False
    )

    max_new_tokens, temperature = model_settings()

    load_buttons(
        current_user_id,
        country, starting_point, query, model, cost_preference, temporary_events,
        weather, carbon_footprint_preference,
        max_new_tokens, temperature,
        start_date, end_date,
        output,
        generate_text_fn=generate_text,
        clear_fn=clear
    )
    
    save_btn = gr.Button("Save to favourites")
    show_profile_btn = gr.Button("Show profile")
    show_profile_btn.click(
        fn=show_user_profile,
        inputs=[current_user_id],
        outputs=[profile_output]
    )
    save_btn.click(
        fn=save_recommendation,
        inputs=[
            current_user_id,
            query,
            starting_point,
            cost_preference,
            temporary_events,
            weather,
            carbon_footprint_preference,
            start_date,
            end_date,
            output,
        ],
        outputs=[save_status],
    )

    # Examples are temporarily disabled because generate_text now requires
    # current_user_id from the login state.
    # load_examples(
    #     country, starting_point, query, model, cost_preference, temporary_events,
    #     weather, carbon_footprint_preference, output, generate_text
    # )
