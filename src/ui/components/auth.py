"""
src/ui/components/auth.py

Standalone login / registration screen for Green City Finder.

Styling now lives in src/ui/components/styles.py (APP_CSS). This module only
builds the components and wires the show/hide between the login screen and the
app screen. Layout rule kept from earlier fixes:

  screen   gr.Column          <- toggled, NO custom class -> hides cleanly
    center gr.Column .gcf-center
      card gr.Group .gcf-auth-card   <- the only intentional panel
"""

from dataclasses import dataclass

import gradio as gr

from src.ui.components.actions import login_user, register_user
# Re-export so any existing `from ...auth import AUTH_CSS` keeps working.



# --------------------------------------------------------------------------- #
# Handlers (output order fixed by connect_auth)
# --------------------------------------------------------------------------- #
def _normalise_email(email: str) -> str:
    return (email or "").strip().lower()


def _validate(email: str, password: str):
    email = _normalise_email(email)
    if not email or "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return "Enter a valid email address, e.g. you@example.com."
    if not password:
        return "Enter your password to continue."
    return None


def _stay(message: str):
    return (
        None,
        gr.update(value=f"⚠️ {message}"),
        gr.update(visible=True),    # login screen
        gr.update(visible=False),   # main_app
        gr.update(value=""),        # welcome
    )


def _enter(user_id, status: str, email: str):
    return (
        user_id,
        gr.update(value=""),
        gr.update(visible=False),   # login screen -> hidden
        gr.update(visible=True),    # main_app -> shown
        gr.update(value=f"🍀 Signed in as **{_normalise_email(email)}**"),
    )


def handle_login(email: str, password: str):
    problem = _validate(email, password)
    if problem:
        return _stay(problem)
    user_id, status = login_user(email, password)
    if user_id is None:
        return _stay(status.replace("Login failed: ", "") or "Invalid email or password.")
    return _enter(user_id, status, email)


def handle_register(email: str, password: str):
    problem = _validate(email, password)
    if problem:
        return _stay(problem)
    if len(password) < 6:
        return _stay("Choose a password with at least 6 characters.")
    user_id, status = register_user(email, password)
    if user_id is None:
        return _stay(status.replace("Registration failed: ", "") or "Could not create the account.")
    return _enter(user_id, status, email)


def handle_logout():
    return (
        None,
        gr.update(value=""),
        gr.update(value="", interactive=True),   # email
        gr.update(value="", interactive=True),   # password
        gr.update(visible=True),                 # login screen
        gr.update(visible=False),                # main_app
        gr.update(value=""),                     # welcome
    )


# --------------------------------------------------------------------------- #
# UI builders
# --------------------------------------------------------------------------- #
@dataclass
class LoginUI:
    current_user_id: gr.State
    screen: gr.Column
    email: gr.Textbox
    password: gr.Textbox
    status: gr.Markdown
    login_btn: gr.Button
    register_btn: gr.Button


@dataclass
class SessionUI:
    bar: gr.Row
    welcome: gr.Markdown
    logout_btn: gr.Button


def login_screen() -> LoginUI:
    current_user_id = gr.State(None)

    with gr.Column(visible=True) as screen:
        with gr.Column(elem_classes="gcf-center"):
            with gr.Group(elem_classes="gcf-auth-card"):
                gr.HTML(
                    '<div class="gcf-auth-head">'
                    '<div class="gcf-wordmark">🍀 Green City Finder</div>'
                    '<p class="gcf-subtitle">Sign in to sync your sustainable travel profile</p>'
                    '</div>'
                )
                email = gr.Textbox(label="Email", placeholder="you@example.com", autofocus=True)
                password = gr.Textbox(label="Password", type="password", placeholder="Your password")
                status = gr.Markdown("", elem_classes="gcf-auth-status")
                with gr.Row():
                    login_btn = gr.Button("Log in", variant="primary")
                    register_btn = gr.Button("Create account", variant="secondary")

    return LoginUI(current_user_id, screen, email, password, status, login_btn, register_btn)


def session_bar() -> SessionUI:
    with gr.Row(elem_classes="gcf-session-bar") as bar:
        welcome = gr.Markdown("", elem_classes="gcf-welcome")
        logout_btn = gr.Button("Log out", scale=0, elem_classes="gcf-logout")
    return SessionUI(bar, welcome, logout_btn)


def connect_auth(login: LoginUI, session: SessionUI, main_app) -> None:
    enter_outputs = [login.current_user_id, login.status, login.screen, main_app, session.welcome]

    login.login_btn.click(handle_login, [login.email, login.password], enter_outputs)
    login.password.submit(handle_login, [login.email, login.password], enter_outputs)
    login.register_btn.click(handle_register, [login.email, login.password], enter_outputs)

    session.logout_btn.click(
        handle_logout,
        inputs=None,
        outputs=[
            login.current_user_id, login.status,
            login.email, login.password,
            login.screen, main_app, session.welcome,
        ],
    )
