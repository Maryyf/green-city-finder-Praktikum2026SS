import gradio as gr

from src.ui.components.actions import (
    AVATAR_OPTIONS,
    get_user_display,
    register_user,
    login_user,
)


SET_COOKIE_AND_SHOW_PAGE_JS = r"""
(token) => {
    if (token) {
        document.cookie =
            "gcf_session_token=" + encodeURIComponent(token) +
            "; Max-Age=2592000; Path=/; SameSite=Lax";
    }

    requestAnimationFrame(() => {
        const auth = document.getElementById("auth-screen");
        const app = document.getElementById("app-shell");

        if (app && window.getComputedStyle(app).display !== "none") {
            if (auth) {
                auth.style.setProperty("display", "none", "important");
                auth.style.setProperty("height", "0", "important");
                auth.style.setProperty("min-height", "0", "important");
                auth.style.setProperty("margin", "0", "important");
                auth.style.setProperty("padding", "0", "important");
                auth.style.setProperty("overflow", "hidden", "important");
            }

            window.scrollTo({top: 0, left: 0, behavior: "instant"});
        }
    });
}
"""


def login_view(email: str, password: str):
    user_id, message, session_token = login_user(email, password)

    if user_id is None:
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            f"❌ {message}",
            "",
            gr.update(value="👤"),
        )

    user = get_user_display(user_id)

    return (
        user_id,
        gr.update(visible=False),
        gr.update(visible=True),
        "",
        session_token,
        gr.update(value=user.get("avatar", "👤")),
    )


def register_view(
    email: str,
    username: str,
    avatar: str,
    password: str,
    confirm_password: str,
):
    if password != confirm_password:
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            "❌ Registration failed: passwords do not match.",
            "",
            gr.update(value="👤"),
        )

    user_id, message, session_token = register_user(
        email=email,
        password=password,
        username=username,
        avatar=avatar,
    )

    if user_id is None:
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            f"❌ {message}",
            "",
            gr.update(value="👤"),
        )

    user = get_user_display(user_id)

    return (
        user_id,
        gr.update(visible=False),
        gr.update(visible=True),
        "",
        session_token,
        gr.update(value=user.get("avatar", "👤")),
    )


def build_auth_form():
    """
    Form 1: login / registration page.
    """
    with gr.Column(visible=True, elem_id="auth-screen") as auth_panel:
        with gr.Row(elem_id="auth-card", equal_height=True):
            with gr.Column(scale=6, elem_classes=["auth-hero"]):
                gr.HTML(
                    """
                    <div class="brand-pill">🍀 GREEN CITY FINDER</div>
                    <h1>Travel better.<br><span>Leave less behind.</span></h1>
                    <p class="auth-hero-copy">
                        Sign in to receive European city recommendations shaped by
                        your travel style, budget, weather preferences and carbon impact.
                    </p>
                    <div class="auth-benefits">
                        <div class="auth-benefit">
                            <span class="auth-benefit-icon">✓</span>
                            Save recommendations to your favourites
                        </div>
                        <div class="auth-benefit">
                            <span class="auth-benefit-icon">✓</span>
                            Build a reusable personal travel profile
                        </div>
                        <div class="auth-benefit">
                            <span class="auth-benefit-icon">✓</span>
                            Compare cost, events, weather and emissions
                        </div>
                    </div>
                    """
                )

            with gr.Column(scale=5, elem_classes=["auth-form"]):
                gr.HTML(
                    """
                    <div class="auth-heading">
                        <h2>Welcome</h2>
                        <p>Sign in to continue, or create an account for this prototype.</p>
                    </div>
                    """
                )

                with gr.Tabs():
                    with gr.Tab("Sign in"):
                        login_email = gr.Textbox(
                            label="Email address",
                            placeholder="name@example.com",
                        )
                        login_password = gr.Textbox(
                            label="Password",
                            type="password",
                            placeholder="Enter your password",
                        )
                        login_btn = gr.Button("Sign in", variant="primary")

                    with gr.Tab("Create account"):
                        register_email = gr.Textbox(
                            label="Email address",
                            placeholder="name@example.com",
                        )
                        register_username = gr.Textbox(
                            label="Username",
                            placeholder="Mary",
                        )
                        register_avatar = gr.Radio(
                            choices=AVATAR_OPTIONS,
                            value="🌿",
                            label="Choose an avatar",
                            elem_classes=["avatar-radio"],
                        )
                        register_password = gr.Textbox(
                            label="Password",
                            type="password",
                            placeholder="At least 8 characters",
                        )
                        confirm_password = gr.Textbox(
                            label="Confirm password",
                            type="password",
                            placeholder="Repeat your password",
                        )
                        register_btn = gr.Button("Create account", variant="primary")

                auth_status = gr.Markdown("", elem_id="auth-status")
                gr.HTML(
                    """
                    <p class="auth-note">
                        Your username and avatar are stored with your local account.
                        Your password is stored as a salted hash, never as plain text.
                    </p>
                    """
                )

    return {
        "panel": auth_panel,
        "status": auth_status,
        "login_email": login_email,
        "login_password": login_password,
        "login_btn": login_btn,
        "register_email": register_email,
        "register_username": register_username,
        "register_avatar": register_avatar,
        "register_password": register_password,
        "confirm_password": confirm_password,
        "register_btn": register_btn,
    }


def bind_auth_events(auth_form: dict, current_user_id, recommendation_form: dict, session_token_store):
    """
    Successful login / registration hides Form 1, shows Form 2 and stores
    the session token in a browser cookie.
    """
    auth_outputs = [
        current_user_id,
        auth_form["panel"],
        recommendation_form["panel"],
        auth_form["status"],
        session_token_store,
        recommendation_form["profile_btn"],
    ]

    login_click = auth_form["login_btn"].click(
        fn=login_view,
        inputs=[auth_form["login_email"], auth_form["login_password"]],
        outputs=auth_outputs,
        show_progress="hidden",
        queue=False,
    )
    login_click.then(
        fn=None,
        inputs=[session_token_store],
        js=SET_COOKIE_AND_SHOW_PAGE_JS,
        show_progress="hidden",
        queue=False,
    )

    login_submit = auth_form["login_password"].submit(
        fn=login_view,
        inputs=[auth_form["login_email"], auth_form["login_password"]],
        outputs=auth_outputs,
        show_progress="hidden",
        queue=False,
    )
    login_submit.then(
        fn=None,
        inputs=[session_token_store],
        js=SET_COOKIE_AND_SHOW_PAGE_JS,
        show_progress="hidden",
        queue=False,
    )

    register_click = auth_form["register_btn"].click(
        fn=register_view,
        inputs=[
            auth_form["register_email"],
            auth_form["register_username"],
            auth_form["register_avatar"],
            auth_form["register_password"],
            auth_form["confirm_password"],
        ],
        outputs=auth_outputs,
        show_progress="hidden",
        queue=False,
    )
    register_click.then(
        fn=None,
        inputs=[session_token_store],
        js=SET_COOKIE_AND_SHOW_PAGE_JS,
        show_progress="hidden",
        queue=False,
    )

    register_submit = auth_form["confirm_password"].submit(
        fn=register_view,
        inputs=[
            auth_form["register_email"],
            auth_form["register_username"],
            auth_form["register_avatar"],
            auth_form["register_password"],
            auth_form["confirm_password"],
        ],
        outputs=auth_outputs,
        show_progress="hidden",
        queue=False,
    )
    register_submit.then(
        fn=None,
        inputs=[session_token_store],
        js=SET_COOKIE_AND_SHOW_PAGE_JS,
        show_progress="hidden",
        queue=False,
    )
