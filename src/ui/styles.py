APP_CSS = """
:root {
    --gcf-forest: #123b2a;
    --gcf-green: #1f7a4d;
    --gcf-green-2: #2a9d63;
    --gcf-mint: #e9f8ef;
    --gcf-mint-2: #f4fbf6;
    --gcf-cream: #f7faf7;
    --gcf-blue: #eaf4fb;
    --gcf-ink: #17322a;
    --gcf-muted: #66766f;
    --gcf-line: #dbe9e0;
    --gcf-shadow: 0 18px 48px rgba(18, 59, 42, 0.10);
}

body {
    background:
        radial-gradient(circle at 12% 8%, rgba(92, 184, 122, 0.14), transparent 28rem),
        radial-gradient(circle at 90% 88%, rgba(67, 139, 202, 0.12), transparent 30rem),
        var(--gcf-cream);
}

.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    background: transparent !important;
}

/* -------------------------- Form 1: auth page -------------------------- */

#auth-screen {
    min-height: 0 !important;
    align-items: center;
    justify-content: center;
    padding: clamp(12px, 4vh, 36px) 12px;
    margin: 0 !important;
}

#auth-screen.hide,
#auth-screen.hidden,
#auth-screen[hidden],
#auth-screen[style*="display: none"] {
    display: none !important;
    min-height: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

#auth-card {
    width: min(1060px, 100%);
    overflow: hidden;
    border: 1px solid rgba(18, 59, 42, 0.10);
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.96);
    box-shadow: 0 28px 80px rgba(18, 59, 42, 0.15);
}

#auth-card > div {
    gap: 0 !important;
}

.auth-hero {
    min-height: 610px;
    padding: 48px !important;
    color: white;
    background:
        linear-gradient(145deg, rgba(9, 48, 32, 0.96), rgba(31, 122, 77, 0.92)),
        radial-gradient(circle at 15% 20%, rgba(255,255,255,0.16), transparent 15rem);
}

.auth-form {
    justify-content: center;
    padding: 46px !important;
    background: white;
}

.brand-pill {
    display: inline-flex;
    width: fit-content;
    align-items: center;
    gap: 8px;
    padding: 9px 14px;
    border: 1px solid rgba(255,255,255,0.24);
    border-radius: 999px;
    background: rgba(255,255,255,0.10);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
}

.auth-hero h1 {
    margin: 64px 0 18px;
    font-size: clamp(42px, 5vw, 66px);
    line-height: 1.02;
    letter-spacing: -0.05em;
}

.auth-hero h1 span {
    color: #baf2cc;
}

.auth-hero-copy {
    max-width: 520px;
    color: rgba(255,255,255,0.78);
    font-size: 17px;
    line-height: 1.7;
}

.auth-benefits {
    display: grid;
    gap: 13px;
    margin-top: 44px;
}

.auth-benefit {
    display: flex;
    align-items: center;
    gap: 12px;
    color: rgba(255,255,255,0.92);
    font-size: 14px;
}

.auth-benefit-icon {
    display: grid;
    width: 30px;
    height: 30px;
    place-items: center;
    border-radius: 10px;
    background: rgba(255,255,255,0.13);
}

.auth-heading h2 {
    margin: 0;
    color: var(--gcf-ink);
    font-size: 32px;
    letter-spacing: -0.035em;
}

.auth-heading p {
    margin: 8px 0 24px;
    color: var(--gcf-muted);
    line-height: 1.55;
}

.auth-note {
    margin-top: 16px;
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.6;
}

#auth-status {
    min-height: 28px;
    margin-top: 10px;
}

#auth-card button.primary {
    min-height: 46px;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

#auth-card input {
    min-height: 44px;
}

/* ---------------------- Form 2: recommendation page --------------------- */

#app-shell {
    min-height: 0 !important;
    margin: 0 !important;
    padding: 18px 4px 52px !important;
}

.recommendation-page {
    gap: 16px !important;
}

.app-topbar {
    position: sticky;
    top: 10px;
    z-index: 20;
    align-items: center;
    margin-bottom: 8px;
    padding: 12px 16px !important;
    border: 1px solid rgba(18, 59, 42, 0.10);
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.88);
    box-shadow: 0 12px 34px rgba(18, 59, 42, 0.08);
    backdrop-filter: blur(16px);
}

.app-brand-block {
    display: flex;
    align-items: center;
    gap: 12px;
}

.app-logo {
    display: grid;
    width: 44px;
    height: 44px;
    place-items: center;
    border-radius: 15px;
    background: linear-gradient(145deg, var(--gcf-green), var(--gcf-forest));
    color: white;
    font-size: 22px;
    box-shadow: 0 10px 22px rgba(31, 122, 77, 0.22);
}

.app-brand-title {
    color: var(--gcf-ink);
    font-size: 19px;
    font-weight: 850;
    letter-spacing: -0.03em;
}

.app-brand-subtitle {
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.3;
}

.profile-entry-column {
    align-items: flex-end;
}

#profile-avatar-button {
    width: 48px !important;
    height: 48px !important;
    min-width: 48px !important;
    padding: 0 !important;
    border: 0 !important;
    border-radius: 999px !important;
    background:
        linear-gradient(145deg, #ffffff, #e9f8ef) !important;
    color: var(--gcf-forest) !important;
    font-size: 22px !important;
    box-shadow:
        inset 0 0 0 1px rgba(31, 122, 77, 0.16),
        0 12px 24px rgba(18, 59, 42, 0.12) !important;
}

#profile-avatar-button:hover {
    transform: translateY(-1px);
    box-shadow:
        inset 0 0 0 1px rgba(31, 122, 77, 0.24),
        0 16px 30px rgba(18, 59, 42, 0.16) !important;
}

.profile-panel {
    margin: -2px 0 2px auto !important;
    max-width: 520px;
    padding: 18px !important;
    border: 1px solid rgba(31, 122, 77, 0.16);
    border-radius: 24px;
    background:
        linear-gradient(145deg, rgba(255,255,255,0.98), rgba(244,251,246,0.98));
    box-shadow: var(--gcf-shadow);
}

.profile-card-header {
    display: flex;
    align-items: center;
    gap: 13px;
}

.profile-card-avatar {
    display: grid;
    width: 56px;
    height: 56px;
    place-items: center;
    border-radius: 999px;
    background: linear-gradient(145deg, var(--gcf-green), var(--gcf-forest));
    color: white;
    font-size: 28px;
    box-shadow: 0 14px 28px rgba(31, 122, 77, 0.24);
}

.profile-card-title {
    color: var(--gcf-ink);
    font-size: 18px;
    font-weight: 850;
    letter-spacing: -0.02em;
}

.profile-card-subtitle {
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.45;
}

#profile-close-button {
    width: 34px !important;
    min-width: 34px !important;
    height: 34px !important;
    padding: 0 !important;
    border-radius: 999px !important;
    border: 1px solid var(--gcf-line) !important;
    background: white !important;
    color: var(--gcf-muted) !important;
    font-size: 20px !important;
}

#profile-content {
    margin-top: 12px;
    padding: 14px 16px;
    border-radius: 16px;
    background: white;
    color: var(--gcf-ink);
    border: 1px solid rgba(18, 59, 42, 0.08);
}

.hero-card,
.main-form-card,
.result-card,
.settings-card,
.intro-accordion {
    border: 1px solid rgba(18, 59, 42, 0.09);
    border-radius: 24px;
    background: rgba(255,255,255,0.92);
    box-shadow: var(--gcf-shadow);
}

.hero-card {
    overflow: hidden;
    padding: 30px 34px !important;
    background:
        linear-gradient(135deg, rgba(233,248,239,0.96), rgba(234,244,251,0.92)),
        radial-gradient(circle at 90% 10%, rgba(31,122,77,0.12), transparent 18rem);
}

.hero-card h2 {
    margin: 8px 0 8px;
    color: var(--gcf-ink);
    font-size: clamp(30px, 4vw, 46px);
    line-height: 1.05;
    letter-spacing: -0.05em;
}

.hero-card p {
    max-width: 780px;
    margin: 0;
    color: var(--gcf-muted);
    font-size: 15px;
    line-height: 1.7;
}

.hero-kicker {
    display: inline-flex;
    width: fit-content;
    padding: 7px 12px;
    border-radius: 999px;
    background: white;
    color: var(--gcf-green);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    box-shadow: 0 8px 18px rgba(18, 59, 42, 0.06);
}

.main-form-card,
.result-card,
.settings-card {
    padding: 20px !important;
}

.result-card textarea {
    min-height: 180px !important;
}

.settings-card {
    margin-bottom: 8px;
}

.save-row {
    justify-content: flex-end;
}

.save-row button.primary {
    border-radius: 14px !important;
    font-weight: 800 !important;
}

.main-form-card input,
.main-form-card textarea,
.main-form-card select,
.result-card textarea,
.settings-card input {
    border-radius: 12px !important;
}

@media (max-width: 820px) {
    .gradio-container {
        max-width: 100% !important;
    }

    #auth-screen {
        align-items: flex-start;
        padding: 12px 2px;
    }

    #auth-card {
        border-radius: 20px;
    }

    .auth-hero {
        min-height: auto;
        padding: 32px !important;
    }

    .auth-hero h1 {
        margin-top: 38px;
        font-size: 42px;
    }

    .auth-form {
        padding: 32px !important;
    }

    #app-shell {
        padding: 10px 0 36px !important;
    }

    .app-topbar {
        top: 4px;
        border-radius: 18px;
    }

    .app-brand-subtitle {
        display: none;
    }

    .profile-panel {
        max-width: none;
        margin: 0 !important;
    }

    .hero-card,
    .main-form-card,
    .result-card,
    .settings-card {
        border-radius: 18px;
        padding: 18px !important;
    }
}

/* ------------------- User metadata + profile bar chart ------------------ */

.avatar-radio .wrap,
.avatar-radio fieldset {
    gap: 8px !important;
}

.avatar-radio label {
    border-radius: 999px !important;
}

.profile-card-email {
    margin: 2px 0 3px;
    color: var(--gcf-muted);
    font-size: 12px;
}

#profile-content {
    margin-top: 12px;
    padding: 14px 16px;
    border-radius: 16px;
    background: white;
    color: var(--gcf-ink);
    border: 1px solid rgba(18, 59, 42, 0.08);
}

.profile-empty-state {
    padding: 14px 12px;
    border-radius: 14px;
    background: var(--gcf-mint-2);
    color: var(--gcf-muted);
    font-size: 13px;
    line-height: 1.6;
}

.profile-bars {
    display: grid;
    gap: 13px;
}

.profile-bar-row {
    display: grid;
    gap: 6px;
}

.profile-bar-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.profile-bar-label {
    color: var(--gcf-ink);
    font-size: 13px;
    font-weight: 750;
}

.profile-bar-score {
    color: var(--gcf-muted);
    font-size: 12px;
    font-variant-numeric: tabular-nums;
}

.profile-bar-track {
    height: 10px;
    overflow: hidden;
    border-radius: 999px;
    background: #eef4f0;
    box-shadow: inset 0 0 0 1px rgba(18, 59, 42, 0.04);
}

.profile-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.25s ease;
}

.bar-beach {
    background: linear-gradient(90deg, #40c9c6, #6ee7f2);
}

.bar-nature {
    background: linear-gradient(90deg, #2f9e44, #8ce99a);
}

.bar-outdoor {
    background: linear-gradient(90deg, #748ffc, #91a7ff);
}

.bar-historic {
    background: linear-gradient(90deg, #b7791f, #f2c94c);
}

.bar-culture {
    background: linear-gradient(90deg, #845ef7, #b197fc);
}

.bar-nightlife {
    background: linear-gradient(90deg, #cc5de8, #f783ac);
}

.bar-food {
    background: linear-gradient(90deg, #ff922b, #ffc078);
}

.bar-shopping {
    background: linear-gradient(90deg, #e64980, #faa2c1);
}

.bar-low-cost {
    background: linear-gradient(90deg, #12b886, #63e6be);
}

.bar-low-carbon {
    background: linear-gradient(90deg, #087f5b, #69db7c);
}

.bar-dry-weather {
    background: linear-gradient(90deg, #fab005, #ffe066);
}

.bar-default {
    background: linear-gradient(90deg, var(--gcf-green), var(--gcf-green-2));
}


/* -------------------------- Username editor ----------------------------- */

.username-editor {
    margin-top: 14px;
    padding: 14px 16px !important;
    border: 1px solid rgba(18, 59, 42, 0.08);
    border-radius: 16px;
    background: rgba(244, 251, 246, 0.82);
}

.username-editor-title {
    color: var(--gcf-ink);
    font-size: 14px;
    font-weight: 850;
    letter-spacing: -0.01em;
}

.username-editor-subtitle {
    margin: 2px 0 10px;
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.45;
}

#username-input input {
    border-radius: 12px !important;
}

.username-actions {
    justify-content: flex-end;
}

#save-username-button {
    border-radius: 12px !important;
    font-weight: 800 !important;
}

#username-status {
    min-height: 24px;
    color: var(--gcf-muted);
    font-size: 12px;
}


/* ---------------------------- Avatar editor ----------------------------- */

.profile-editor-grid {
    display: grid;
    gap: 12px;
}

.avatar-editor,
.username-editor {
    margin-top: 14px;
    padding: 14px 16px !important;
    border: 1px solid rgba(18, 59, 42, 0.08);
    border-radius: 16px;
    background: rgba(244, 251, 246, 0.82);
}

.profile-editor-title,
.username-editor-title {
    color: var(--gcf-ink);
    font-size: 14px;
    font-weight: 850;
    letter-spacing: -0.01em;
}

.profile-editor-subtitle,
.username-editor-subtitle {
    margin: 2px 0 10px;
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.45;
}

.profile-editor-actions,
.username-actions {
    justify-content: flex-end;
}

#save-avatar-button,
#save-username-button {
    border-radius: 12px !important;
    font-weight: 800 !important;
}

#avatar-status,
#username-status {
    min-height: 24px;
    color: var(--gcf-muted);
    font-size: 12px;
}

.avatar-editor-radio .wrap,
.avatar-editor-radio fieldset,
.avatar-radio .wrap,
.avatar-radio fieldset {
    gap: 8px !important;
}

.avatar-editor-radio label,
.avatar-radio label {
    border-radius: 999px !important;
}

@media (min-width: 880px) {
    .profile-editor-grid {
        grid-template-columns: 1fr 1fr;
    }
}


/* ------------------------ Cookie session helpers ------------------------ */

.cookie-helper {
    display: none !important;
}

/* ---------------------- Travel Preference title ------------------------- */

.travel-preference-title {
    margin: 2px 0 14px;
    color: var(--gcf-ink);
    font-size: 15px;
    font-weight: 900;
    letter-spacing: -0.02em;
}

/* In case the current style file does not yet contain the editor CSS. */
.profile-editor-grid {
    display: grid;
    gap: 12px;
}

.avatar-editor,
.username-editor {
    margin-top: 14px;
    padding: 14px 16px !important;
    border: 1px solid rgba(18, 59, 42, 0.08);
    border-radius: 16px;
    background: rgba(244, 251, 246, 0.82);
}

.profile-editor-title,
.username-editor-title {
    color: var(--gcf-ink);
    font-size: 14px;
    font-weight: 850;
    letter-spacing: -0.01em;
}

.profile-editor-subtitle,
.username-editor-subtitle {
    margin: 2px 0 10px;
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.45;
}

.profile-editor-actions,
.username-actions {
    justify-content: flex-end;
}

#save-avatar-button,
#save-username-button {
    border-radius: 12px !important;
    font-weight: 800 !important;
}

#avatar-status,
#username-status {
    min-height: 24px;
    color: var(--gcf-muted);
    font-size: 12px;
}

.avatar-editor-radio .wrap,
.avatar-editor-radio fieldset,
.avatar-radio .wrap,
.avatar-radio fieldset {
    gap: 8px !important;
}

.avatar-editor-radio label,
.avatar-radio label {
    border-radius: 999px !important;
}

@media (min-width: 880px) {
    .profile-editor-grid {
        grid-template-columns: 1fr 1fr;
    }
}


/* ------------------------------- Logout -------------------------------- */

.topbar-actions {
    justify-content: flex-end;
    align-items: center;
    gap: 10px !important;
}

#logout-button {
    min-width: 84px !important;
    height: 42px !important;
    padding: 0 16px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(18, 59, 42, 0.12) !important;
    background: rgba(255, 255, 255, 0.78) !important;
    color: var(--gcf-forest) !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    box-shadow: 0 10px 22px rgba(18, 59, 42, 0.07) !important;
}

#logout-button:hover {
    transform: translateY(-1px);
    background: #fff !important;
    box-shadow: 0 14px 28px rgba(18, 59, 42, 0.12) !important;
}

@media (max-width: 820px) {
    #logout-button {
        min-width: 72px !important;
        padding: 0 12px !important;
        font-size: 12px !important;
    }

    .topbar-actions {
        gap: 8px !important;
    }
}

"""
