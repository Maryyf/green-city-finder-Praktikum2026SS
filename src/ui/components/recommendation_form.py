import gradio as gr

from src.ui.components.actions import (
    AVATAR_OPTIONS,
    BOOKMARK_ROW_LIMIT,
    clear,
    delete_bookmark,
    generate_text,
    get_user_display,
    logout_user,
    refresh_bookmarks_page,
    render_profile_bars,
    render_profile_header,
    save_recommendation,
    update_avatar,
    update_username,
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


def _flatten_bookmark_row_outputs(bookmark_rows):
    outputs = []

    for row, bookmark_html, bookmark_id_state, _delete_btn in bookmark_rows:
        outputs.extend([row, bookmark_html, bookmark_id_state])

    return outputs


def load_profile_tab(current_user_id):
    user = get_user_display(current_user_id)

    return (
        render_profile_header(current_user_id),
        render_profile_bars(current_user_id),
        user.get("username", ""),
        "",
        user.get("avatar", "👤"),
        "",
    )


def open_profile_tab(current_user_id):
    return (
        gr.update(selected="profile"),
        *load_profile_tab(current_user_id),
    )


def build_recommendation_form(
    current_user_id,
    auth_panel=None,
    auth_status=None,
    session_token_store=None,
    intro_html: str = "",
):
    """Build the authenticated Discover, Saved and Profile workspace."""
    with gr.Column(
        visible=False,
        elem_id="app-shell",
        elem_classes=["recommendation-page"],
    ) as recommendation_panel:
        with gr.Row(elem_classes=["app-topbar"]):
            with gr.Column(scale=7, min_width=260):
                gr.HTML(
                    """
                    <div class="app-brand-block">
                        <div class="app-logo">🌿</div>
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

        # Kept only as a compatibility output for the existing logout callback.
        with gr.Column(visible=False, elem_classes=["cookie-helper"]) as profile_panel:
            gr.HTML("")

        with gr.Tabs(
            selected="discover",
            elem_id="app-tabs",
            elem_classes=["workspace-tabs"],
        ) as app_tabs:
            with gr.Tab("Discover", id="discover", elem_id="discover-tab"):
                with gr.Row(elem_classes=["tab-page-heading"]):
                    gr.HTML(
                        """
                        <div>
                            <div class="workspace-kicker">Discover</div>
                            <h2>Plan a greener city break</h2>
                        </div>
                        """
                    )

                if intro_html:
                    with gr.Accordion(
                        "About this project",
                        open=False,
                        elem_classes=["intro-accordion"],
                    ):
                        gr.HTML(intro_html)

                with gr.Row(elem_classes=["discover-layout"]):
                    with gr.Column(
                        scale=4,
                        min_width=390,
                        elem_classes=["discover-filter-panel"],
                    ):
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

                        with gr.Row(elem_classes=["query-preset-row"]):
                            history_example_btn = gr.Button(
                                "Museums & history",
                                size="sm",
                                variant="secondary",
                            )
                            nature_example_btn = gr.Button(
                                "Nature & hiking",
                                size="sm",
                                variant="secondary",
                            )

                        max_new_tokens, temperature = model_settings()

                        with gr.Row(elem_classes=["search-button-group"]):
                            submit_btn = gr.Button("Search", variant="primary")
                            clear_btn = gr.Button("Clear", variant="secondary")

                    with gr.Column(
                        scale=6,
                        min_width=420,
                        elem_classes=["discover-result-panel"],
                    ):
                        output = gr.Markdown(
                            "Select your preferences and run a search.",
                            elem_id="markdown-recommendation-output",
                        )

                        with gr.Row(elem_classes=["result-actions"]):
                            save_btn = gr.Button(
                                "Save to favourites",
                                variant="primary",
                            )

                        save_status = gr.Textbox(
                            label="Save status",
                            interactive=False,
                            elem_classes=["save-status"],
                        )

            with gr.Tab("Saved", id="saved", elem_id="saved-tab") as saved_tab:
                with gr.Row(elem_classes=["tab-page-heading"]):
                    gr.HTML(
                        """
                        <div>
                            <div class="workspace-kicker">Saved</div>
                            <h2>Your travel bookmarks</h2>
                        </div>
                        """
                    )

                with gr.Column(elem_classes=["bookmarks-page-card"]):
                    bookmarks_status = gr.HTML(
                        """
                        <div class="bookmark-helper">
                            Open this tab to load saved recommendations.
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
                            with gr.Column(
                                scale=1,
                                min_width=110,
                                elem_classes=["bookmark-real-delete-column"],
                            ):
                                delete_btn = gr.Button(
                                    "Delete",
                                    elem_id=f"bookmark-delete-button-{index}",
                                    elem_classes=["bookmark-real-delete-button"],
                                )

                        bookmark_id_state = gr.State(None)
                        bookmark_rows.append(
                            (bookmark_row, bookmark_html, bookmark_id_state, delete_btn)
                        )

            with gr.Tab("Profile", id="profile", elem_id="profile-tab") as profile_tab:
                with gr.Row(elem_classes=["tab-page-heading"]):
                    gr.HTML(
                        """
                        <div>
                            <div class="workspace-kicker">Profile</div>
                            <h2>Your travel preferences</h2>
                        </div>
                        """
                    )

                with gr.Column(elem_classes=["profile-tab-card"]):
                    profile_header = gr.HTML()
                    profile_output = gr.HTML("", elem_id="profile-content")

                    with gr.Row(elem_classes=["profile-editor-grid"]):
                        with gr.Column(elem_classes=["username-editor"]):
                            gr.HTML('<div class="profile-editor-title">Username</div>')
                            username_input = gr.Textbox(
                                label="Username",
                                placeholder="Enter a new username",
                                max_lines=1,
                                elem_id="username-input",
                            )
                            save_username_btn = gr.Button(
                                "Save username",
                                variant="primary",
                                elem_id="save-username-button",
                            )
                            username_status = gr.Markdown("", elem_id="username-status")

                        with gr.Column(elem_classes=["avatar-editor"]):
                            gr.HTML('<div class="profile-editor-title">Avatar</div>')
                            avatar_input = gr.Radio(
                                choices=AVATAR_OPTIONS,
                                value="👤",
                                label="Avatar",
                                elem_classes=["avatar-radio", "avatar-editor-radio"],
                            )
                            save_avatar_btn = gr.Button(
                                "Save avatar",
                                variant="primary",
                                elem_id="save-avatar-button",
                            )
                            avatar_status = gr.Markdown("", elem_id="avatar-status")

        bookmark_row_outputs = _flatten_bookmark_row_outputs(bookmark_rows)

        search_inputs = [
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
        ]

        submit_btn.click(fn=generate_text, inputs=search_inputs, outputs=[output])
        query.submit(fn=generate_text, inputs=search_inputs, outputs=[output])

        clear_btn.click(
            fn=clear,
            inputs=[query, output, save_status],
            outputs=[query, output, save_status],
        )

        history_example_btn.click(
            fn=lambda: "I enjoy museums, history, heritage and architecture.",
            outputs=[query],
            queue=False,
        )
        nature_example_btn.click(
            fn=lambda: "I enjoy mountains, hiking, forests and wildlife.",
            outputs=[query],
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

        saved_tab.select(
            fn=refresh_bookmarks_page,
            inputs=[current_user_id],
            outputs=[bookmarks_status, *bookmark_row_outputs],
            show_progress="hidden",
            queue=False,
        )

        for _row, _bookmark_html, bookmark_id_state, delete_btn in bookmark_rows:
            delete_btn.click(
                fn=delete_bookmark,
                inputs=[current_user_id, bookmark_id_state],
                outputs=[bookmarks_status, *bookmark_row_outputs],
                show_progress="hidden",
                queue=False,
            )

        profile_tab.select(
            fn=load_profile_tab,
            inputs=[current_user_id],
            outputs=[
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

        profile_btn.click(
            fn=open_profile_tab,
            inputs=[current_user_id],
            outputs=[
                app_tabs,
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
