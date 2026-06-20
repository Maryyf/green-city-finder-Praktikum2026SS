import gradio as gr

from src.ui.components.actions import restore_session_from_cookie
from src.ui.components.auth_form import build_auth_form, bind_auth_events
from src.ui.components.recommendation_form import build_recommendation_form


READ_COOKIE_JS = r"""
() => {
    const cookieName = "gcf_session_token";
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (const item of cookies) {
        const cookie = item.trim();

        if (cookie.startsWith(cookieName + "=")) {
            return decodeURIComponent(cookie.substring(cookieName.length + 1));
        }
    }

    return "";
}
"""

SHOW_RESTORED_PAGE_JS = r"""
(token) => {
    requestAnimationFrame(() => {
        const auth = document.getElementById("auth-screen");
        const app = document.getElementById("app-shell");

        if (token) {
            if (auth) {
                auth.style.setProperty("display", "none", "important");
                auth.style.setProperty("height", "0", "important");
                auth.style.setProperty("min-height", "0", "important");
                auth.style.setProperty("margin", "0", "important");
                auth.style.setProperty("padding", "0", "important");
                auth.style.setProperty("overflow", "hidden", "important");
            }

            if (app) {
                app.style.removeProperty("display");
                app.style.removeProperty("height");
                app.style.removeProperty("min-height");
                app.style.removeProperty("margin");
                app.style.removeProperty("padding");
                app.style.removeProperty("overflow");

                app.style.setProperty("display", "flex", "important");
                app.style.setProperty("flex-direction", "column", "important");
            }

            window.scrollTo({top: 0, left: 0, behavior: "instant"});
        }
    });
}
"""


def form_block(intro_html: str = "", app=None):
    """
    Page coordinator.

    Form 1:
        auth_form.py -> login / registration page

    Form 2:
        recommendation_form.py -> recommendation page with editable
        username, avatar, logout, cookie session restore and preference bars.
    """
    current_user_id = gr.State(None)

    session_token_store = gr.Textbox(
        value="",
        elem_id="gcf-session-token",
        elem_classes=["cookie-helper"],
        show_label=False,
    )

    auth_form = build_auth_form()

    recommendation_form = build_recommendation_form(
        current_user_id=current_user_id,
        auth_panel=auth_form["panel"],
        auth_status=auth_form["status"],
        session_token_store=session_token_store,
        intro_html=intro_html,
    )

    bind_auth_events(
        auth_form=auth_form,
        current_user_id=current_user_id,
        recommendation_form=recommendation_form,
        session_token_store=session_token_store,
    )

    restore_outputs = [
        current_user_id,
        auth_form["panel"],
        recommendation_form["panel"],
        auth_form["status"],
        session_token_store,
        recommendation_form["profile_btn"],
    ]

    components = {
        "current_user_id": current_user_id,
        "session_token_store": session_token_store,
        "auth_form": auth_form,
        "recommendation_form": recommendation_form,
        "restore_outputs": restore_outputs,
    }

    if app is not None:
        restore_event = app.load(
            fn=restore_session_from_cookie,
            inputs=[session_token_store],
            outputs=restore_outputs,
            js=READ_COOKIE_JS,
            show_progress="hidden",
            queue=False,
        )

        restore_event.then(
            fn=None,
            inputs=[session_token_store],
            js=SHOW_RESTORED_PAGE_JS,
            show_progress="hidden",
            queue=False,
        )

    return components
