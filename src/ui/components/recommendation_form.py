import gradio as gr

from src.ui.components.actions import (
    AVATAR_OPTIONS,
    generate_text,
    clear,
    get_user_display,
    render_profile_header,
    render_profile_bars,
    save_recommendation,
    update_avatar,
    update_username,
    logout_user,
)
from src.ui.components.inputs import main_component
from src.ui.components.static import model_settings, load_buttons


CLEAR_COOKIE_AND_SHOW_LOGIN_JS = r"""
() => {
    document.cookie =
        "gcf_session_token=; Max-Age=0; Path=/; SameSite=Lax";

    requestAnimationFrame(() => {
        const auth = document.getElementById("auth-screen");
        const app = document.getElementById("app-shell");

        if (app) {
            app.style.setProperty("display", "none", "important");
            app.style.setProperty("height", "0", "important");
            app.style.setProperty("min-height", "0", "important");
            app.style.setProperty("margin", "0", "important");
            app.style.setProperty("padding", "0", "important");
            app.style.setProperty("overflow", "hidden", "important");
        }

        if (auth) {
            auth.style.removeProperty("display");
            auth.style.removeProperty("height");
            auth.style.removeProperty("min-height");
            auth.style.removeProperty("margin");
            auth.style.removeProperty("padding");
            auth.style.removeProperty("overflow");
        }

        window.scrollTo({top: 0, left: 0, behavior: "instant"});
    });
}
"""


def open_profile_panel(current_user_id):
    user = get_user_display(current_user_id)

    return (
        gr.update(visible=True),
        render_profile_header(current_user_id),
        render_profile_bars(current_user_id),
        user.get("username", ""),
        "",
        user.get("avatar", "👤"),
        "",
    )


def close_profile_panel():
    return gr.update(visible=False)


def build_recommendation_form(current_user_id, auth_panel=None, auth_status=None, session_token_store=None, intro_html: str = ""):
    """
    Form 2: polished recommendation page with editable username, avatar and logout.
    """
    with gr.Column(visible=False, elem_id="app-shell", elem_classes=["recommendation-page"]) as recommendation_panel:
        with gr.Row(elem_classes=["app-topbar"]):
            with gr.Column(scale=7, min_width=260):
                gr.HTML(
                    """
                    <div class="app-brand-block">
                        <div class="app-logo">🍀</div>
                        <div>
                            <div class="app-brand-title">Green City Finder</div>
                            <div class="app-brand-subtitle">
                                Sustainable European travel recommendations
                            </div>
                        </div>
                    </div>
                    """
                )

            with gr.Column(scale=3, min_width=180, elem_classes=["profile-entry-column"]):
                with gr.Row(elem_classes=["topbar-actions"]):
                    logout_btn = gr.Button(
                        "Logout",
                        elem_id="logout-button",
                        elem_classes=["logout-button"],
                    )
                    profile_btn = gr.Button(
                        "👤",
                        elem_id="profile-avatar-button",
                        elem_classes=["avatar-button"],
                    )

        with gr.Column(visible=False, elem_id="profile-panel", elem_classes=["profile-panel"]) as profile_panel:
            with gr.Row():
                with gr.Column(scale=8):
                    profile_header = gr.HTML()
                with gr.Column(scale=1, min_width=70):
                    close_profile_btn = gr.Button("×", elem_id="profile-close-button")

            with gr.Column(elem_classes=["profile-editor-grid"]):
                with gr.Column(elem_classes=["username-editor"]):
                    gr.HTML(
                        """
                        <div class="profile-editor-title">Edit username</div>
                        <div class="profile-editor-subtitle">
                            This name is shown in your travel profile.
                        </div>
                        """
                    )
                    username_input = gr.Textbox(
                        label="Username",
                        placeholder="Enter a new username",
                        max_lines=1,
                        elem_id="username-input",
                    )
                    with gr.Row(elem_classes=["profile-editor-actions"]):
                        save_username_btn = gr.Button(
                            "Save username",
                            variant="primary",
                            elem_id="save-username-button",
                        )
                    username_status = gr.Markdown("", elem_id="username-status")

                with gr.Column(elem_classes=["avatar-editor"]):
                    gr.HTML(
                        """
                        <div class="profile-editor-title">Change avatar</div>
                        <div class="profile-editor-subtitle">
                            Choose an avatar for the profile button and profile card.
                        </div>
                        """
                    )
                    avatar_input = gr.Radio(
                        choices=AVATAR_OPTIONS,
                        value="👤",
                        label="Avatar",
                        elem_classes=["avatar-radio", "avatar-editor-radio"],
                    )
                    with gr.Row(elem_classes=["profile-editor-actions"]):
                        save_avatar_btn = gr.Button(
                            "Save avatar",
                            variant="primary",
                            elem_id="save-avatar-button",
                        )
                    avatar_status = gr.Markdown("", elem_id="avatar-status")

            profile_output = gr.HTML(
                "",
                elem_id="profile-content",
            )

        with gr.Column(elem_classes=["hero-card"]):
            gr.HTML(
                """
                <div class="hero-kicker">AI travel assistant</div>
                <h2>Find your next greener city break</h2>
                <p>
                    Describe the kind of trip you want. The system combines city context,
                    cost of living, weather, temporary events and carbon footprint to
                    generate personalised recommendations.
                </p>
                """
            )

        if intro_html:
            with gr.Accordion("About this project", open=False, elem_classes=["intro-accordion"]):
                gr.HTML(intro_html)

        with gr.Column(elem_classes=["main-form-card"]):
            (
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
            ) = main_component()

        with gr.Column(elem_classes=["result-card"]):
            output = gr.Textbox(
                label=(
                    "Your recommendations are sustainable with respect to the "
                    "environment, your starting location, and month of travel."
                ),
                lines=6,
            )

            save_status = gr.Textbox(
                label="Save status",
                interactive=False,
            )

            with gr.Row(elem_classes=["save-row"]):
                save_btn = gr.Button("Save to favourites", variant="primary")

        with gr.Column(elem_classes=["settings-card"]):
            max_new_tokens, temperature = model_settings()

            load_buttons(
                current_user_id,
                country,
                starting_point,
                query,
                model,
                cost_preference,
                temporary_events,
                weather,
                carbon_footprint_preference,
                max_new_tokens,
                temperature,
                start_date,
                end_date,
                output,
                generate_text_fn=generate_text,
                clear_fn=clear,
            )

        profile_btn.click(
            fn=open_profile_panel,
            inputs=[current_user_id],
            outputs=[
                profile_panel,
                profile_header,
                profile_output,
                username_input,
                username_status,
                avatar_input,
                avatar_status,
            ],
            show_progress="hidden",
            queue=False,
        )

        close_profile_btn.click(
            fn=close_profile_panel,
            inputs=[],
            outputs=[profile_panel],
            show_progress="hidden",
            queue=False,
        )

        save_username_btn.click(
            fn=update_username,
            inputs=[current_user_id, username_input],
            outputs=[profile_header, username_status, username_input],
            show_progress="hidden",
            queue=False,
        )

        username_input.submit(
            fn=update_username,
            inputs=[current_user_id, username_input],
            outputs=[profile_header, username_status, username_input],
            show_progress="hidden",
            queue=False,
        )

        save_avatar_btn.click(
            fn=update_avatar,
            inputs=[current_user_id, avatar_input],
            outputs=[profile_header, avatar_status, avatar_input, profile_btn],
            show_progress="hidden",
            queue=False,
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

        if auth_panel is not None and auth_status is not None and session_token_store is not None:
            logout_event = logout_btn.click(
                fn=logout_user,
                inputs=[session_token_store],
                outputs=[
                    current_user_id,
                    auth_panel,
                    recommendation_panel,
                    auth_status,
                    session_token_store,
                    profile_btn,
                    profile_panel,
                ],
                show_progress="hidden",
                queue=False,
            )

            logout_event.then(
                fn=None,
                js=CLEAR_COOKIE_AND_SHOW_LOGIN_JS,
                show_progress="hidden",
                queue=False,
            )

    return {
        "panel": recommendation_panel,
        "profile_btn": profile_btn,
        "logout_btn": logout_btn,
        "profile_panel": profile_panel,
    }
