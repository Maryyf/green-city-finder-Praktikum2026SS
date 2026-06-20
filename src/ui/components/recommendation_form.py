import gradio as gr

from src.ui.components.actions import (
    AVATAR_OPTIONS,
    BOOKMARK_ROW_LIMIT,
    generate_text,
    clear,
    get_user_display,
    render_profile_header,
    render_profile_bars,
    save_recommendation,
    update_avatar,
    update_username,
    logout_user,
    open_bookmarks_page,
    back_to_recommendation_page,
    delete_bookmark,
)
from src.ui.components.inputs import main_component
from src.ui.components.static import model_settings


CLEAR_COOKIE_AND_SHOW_LOGIN_JS = r"""
() => {
    document.cookie =
        "gcf_session_token=; Max-Age=0; Path=/; SameSite=Lax";

    requestAnimationFrame(() => {
        const auth = document.getElementById("auth-screen");
        const app = document.getElementById("app-shell");

        if (app) {
            app.style.removeProperty("display");
            app.style.removeProperty("height");
            app.style.removeProperty("min-height");
            app.style.removeProperty("margin");
            app.style.removeProperty("padding");
            app.style.removeProperty("overflow");
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


def _flatten_bookmark_row_outputs(bookmark_rows):
    outputs = []

    for row, bookmark_html, bookmark_id_state, _delete_btn in bookmark_rows:
        outputs.extend([row, bookmark_html, bookmark_id_state])

    return outputs


def build_recommendation_form(current_user_id, auth_panel=None, auth_status=None, session_token_store=None, intro_html: str = ""):
    """
    Form 2: recommendation page with editable username, avatar, logout
    and a separate Bookmarks page.
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

            with gr.Row(elem_classes=["bookmarks-button-row"]):
                bookmarks_btn = gr.Button(
                    "My bookmarks",
                    elem_id="my-bookmarks-button",
                    elem_classes=["my-bookmarks-button"],
                )

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

        with gr.Column(visible=True, elem_id="main-recommendation-page") as main_content:
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
                output = gr.Markdown(
                    """
                    Enter your trip preferences and click Search to generate recommendations.
                    """,
                    elem_id="markdown-recommendation-output",
                )

                save_status = gr.Textbox(
                    label="Save status",
                    interactive=False,
                )

                with gr.Row(elem_classes=["save-row"]):
                    save_btn = gr.Button("Save to favourites", variant="primary")

            with gr.Column(elem_classes=["settings-card"]):
                max_new_tokens, temperature = model_settings()

                with gr.Group(elem_classes=["search-button-group"]) as btns:
                    with gr.Row():
                        submit_btn = gr.Button("Search", variant="primary")
                        clear_btn = gr.Button("Clear", variant="secondary")
                        cancel_btn = gr.Button("Cancel", variant="stop")

                submit_btn.click(
                    fn=generate_text,
                    inputs=[
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
                    ],
                    outputs=[output],
                )

                clear_btn.click(
                    fn=clear,
                    inputs=[
                        query,
                        model,
                        starting_point,
                        country,
                        cost_preference,
                        temporary_events,
                        weather,
                        carbon_footprint_preference,
                        output,
                        save_status,
                    ],
                    outputs=[
                        query,
                        model,
                        starting_point,
                        country,
                        cost_preference,
                        temporary_events,
                        weather,
                        carbon_footprint_preference,
                        output,
                        save_status,
                    ],
                )

                cancel_btn.click(
                    fn=clear,
                    inputs=[
                        query,
                        model,
                        starting_point,
                        country,
                        cost_preference,
                        temporary_events,
                        weather,
                        carbon_footprint_preference,
                        output,
                        save_status,
                    ],
                    outputs=[
                        query,
                        model,
                        starting_point,
                        country,
                        cost_preference,
                        temporary_events,
                        weather,
                        carbon_footprint_preference,
                        output,
                        save_status,
                    ],
                )

        with gr.Column(visible=False, elem_id="bookmarks-page", elem_classes=["bookmarks-page"]) as bookmarks_page:
            with gr.Row(elem_classes=["bookmarks-page-topbar"]):
                with gr.Column(scale=7):
                    gr.HTML(
                        """
                        <div class="bookmarks-page-kicker">Saved recommendations</div>
                        <h2>My bookmarks</h2>
                        <p>
                            Review your saved travel recommendations. Click one item to
                            open the full result, and click it again to collapse the result.
                        </p>
                        """
                    )
                with gr.Column(scale=2, min_width=140, elem_classes=["bookmarks-back-column"]):
                    back_btn = gr.Button(
                        "← Back",
                        elem_id="bookmarks-back-button",
                    )

            with gr.Column(elem_classes=["bookmarks-page-card"]):
                bookmarks_status = gr.HTML(
                    """
                    <div class="bookmark-helper">
                        Select <strong>My bookmarks</strong> to view saved recommendations.
                    </div>
                    """,
                    elem_id="bookmarks-status",
                )

                bookmark_rows = []

                for index in range(BOOKMARK_ROW_LIMIT):
                    with gr.Row(
                        visible=False,
                        elem_classes=["bookmark-real-row"],
                        elem_id=f"bookmark-row-{index}",
                    ) as bookmark_row:
                        with gr.Column(scale=9, elem_classes=["bookmark-real-card-column"]):
                            bookmark_html = gr.HTML(
                                "",
                                elem_id=f"bookmark-html-{index}",
                            )
                        with gr.Column(scale=1, min_width=110, elem_classes=["bookmark-real-delete-column"]):
                            delete_btn = gr.Button(
                                "Delete",
                                elem_id=f"bookmark-delete-button-{index}",
                                elem_classes=["bookmark-real-delete-button"],
                            )

                    bookmark_id_state = gr.State(None)
                    bookmark_rows.append(
                        (
                            bookmark_row,
                            bookmark_html,
                            bookmark_id_state,
                            delete_btn,
                        )
                    )

        bookmark_row_outputs = _flatten_bookmark_row_outputs(bookmark_rows)

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

        bookmarks_btn.click(
            fn=open_bookmarks_page,
            inputs=[current_user_id],
            outputs=[
                main_content,
                bookmarks_page,
                profile_panel,
                bookmarks_status,
                *bookmark_row_outputs,
            ],
            show_progress="hidden",
            queue=False,
        )

        back_btn.click(
            fn=back_to_recommendation_page,
            inputs=[],
            outputs=[
                main_content,
                bookmarks_page,
                bookmarks_status,
                *bookmark_row_outputs,
            ],
            show_progress="hidden",
            queue=False,
        )

        for _row, _bookmark_html, bookmark_id_state, delete_btn in bookmark_rows:
            delete_btn.click(
                fn=delete_bookmark,
                inputs=[current_user_id, bookmark_id_state],
                outputs=[
                    bookmarks_status,
                    *bookmark_row_outputs,
                ],
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
