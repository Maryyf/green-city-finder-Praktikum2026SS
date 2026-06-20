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


/* ------------------------------ Bookmarks ------------------------------- */

.bookmarks-button-row {
    justify-content: flex-end;
    margin-top: 12px;
}

#my-bookmarks-button {
    min-height: 40px !important;
    padding: 0 16px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(31, 122, 77, 0.18) !important;
    background: linear-gradient(145deg, #ffffff, var(--gcf-mint-2)) !important;
    color: var(--gcf-forest) !important;
    font-size: 13px !important;
    font-weight: 850 !important;
    box-shadow: 0 10px 22px rgba(18, 59, 42, 0.07) !important;
}

#my-bookmarks-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 28px rgba(18, 59, 42, 0.12) !important;
}

.bookmarks-panel {
    margin-top: 14px;
    padding: 16px !important;
    border: 1px solid rgba(18, 59, 42, 0.08);
    border-radius: 18px;
    background:
        linear-gradient(145deg, rgba(255,255,255,0.96), rgba(244,251,246,0.92));
}

.bookmarks-title {
    color: var(--gcf-ink);
    font-size: 16px;
    font-weight: 900;
    letter-spacing: -0.02em;
}

.bookmarks-subtitle {
    margin: 3px 0 12px;
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.45;
}

.bookmark-list label {
    border-radius: 14px !important;
}

.bookmark-helper,
.bookmark-empty-state {
    margin-top: 10px;
    padding: 13px 14px;
    border-radius: 14px;
    background: white;
    color: var(--gcf-muted);
    border: 1px solid rgba(18, 59, 42, 0.07);
    font-size: 13px;
    line-height: 1.55;
}

.bookmark-detail-card {
    margin-top: 12px;
    padding: 16px;
    border-radius: 18px;
    background: white;
    border: 1px solid rgba(18, 59, 42, 0.08);
    box-shadow: 0 12px 28px rgba(18, 59, 42, 0.06);
}

.bookmark-detail-meta {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: var(--gcf-muted);
    font-size: 12px;
}

.bookmark-detail-meta strong {
    color: var(--gcf-green);
    font-weight: 800;
}

.bookmark-detail-title {
    margin-top: 8px;
    color: var(--gcf-ink);
    font-size: 16px;
    font-weight: 900;
    line-height: 1.35;
}

.bookmark-detail-start {
    margin-top: 8px;
    color: var(--gcf-muted);
    font-size: 13px;
}

.bookmark-context {
    display: grid;
    gap: 7px;
    margin-top: 12px;
    padding: 12px;
    border-radius: 14px;
    background: var(--gcf-mint-2);
}

.bookmark-context-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: var(--gcf-muted);
    font-size: 12px;
}

.bookmark-context-row strong {
    color: var(--gcf-ink);
    font-weight: 800;
    text-align: right;
}

.bookmark-result-title {
    margin-top: 14px;
    color: var(--gcf-ink);
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.bookmark-result-body {
    margin-top: 8px;
    color: var(--gcf-ink);
    font-size: 13px;
    line-height: 1.7;
}


/* -------------------------- Bookmark toggles ---------------------------- */

.bookmark-list label {
    display: flex !important;
    align-items: flex-start !important;
    gap: 10px !important;
    padding: 10px 12px !important;
    margin-bottom: 8px !important;
    border: 1px solid rgba(18, 59, 42, 0.08) !important;
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.82) !important;
    color: var(--gcf-ink) !important;
    line-height: 1.45 !important;
}

.bookmark-list label:hover {
    background: var(--gcf-mint-2) !important;
    border-color: rgba(31, 122, 77, 0.20) !important;
}

.bookmark-list input[type="checkbox"] {
    margin-top: 3px !important;
}

/* -------------------------- Separate bookmarks page --------------------- */

#main-recommendation-page {
    gap: 16px !important;
}

.bookmarks-page {
    gap: 16px !important;
}

.bookmarks-page-topbar {
    align-items: stretch;
    padding: 28px 32px !important;
    border: 1px solid rgba(18, 59, 42, 0.09);
    border-radius: 26px;
    background:
        linear-gradient(135deg, rgba(233,248,239,0.98), rgba(234,244,251,0.94)),
        radial-gradient(circle at 92% 10%, rgba(31,122,77,0.12), transparent 18rem);
    box-shadow: var(--gcf-shadow);
}

.bookmarks-page-kicker {
    display: inline-flex;
    width: fit-content;
    padding: 7px 12px;
    border-radius: 999px;
    background: white;
    color: var(--gcf-green);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}

.bookmarks-page-topbar h2 {
    margin: 10px 0 8px;
    color: var(--gcf-ink);
    font-size: clamp(30px, 4vw, 44px);
    line-height: 1.05;
    letter-spacing: -0.05em;
}

.bookmarks-page-topbar p {
    max-width: 720px;
    margin: 0;
    color: var(--gcf-muted);
    font-size: 15px;
    line-height: 1.65;
}

.bookmarks-back-column {
    justify-content: flex-start;
    align-items: flex-end;
}

#bookmarks-back-button {
    min-height: 44px !important;
    padding: 0 18px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(18, 59, 42, 0.12) !important;
    background: rgba(255, 255, 255, 0.86) !important;
    color: var(--gcf-forest) !important;
    font-size: 13px !important;
    font-weight: 900 !important;
    box-shadow: 0 12px 24px rgba(18, 59, 42, 0.08) !important;
}

#bookmarks-back-button:hover {
    transform: translateY(-1px);
    background: white !important;
    box-shadow: 0 16px 30px rgba(18, 59, 42, 0.13) !important;
}

.bookmarks-page-card {
    padding: 20px !important;
    border: 1px solid rgba(18, 59, 42, 0.09);
    border-radius: 24px;
    background: rgba(255,255,255,0.94);
    box-shadow: var(--gcf-shadow);
}

@media (max-width: 820px) {
    .bookmarks-page-topbar {
        padding: 20px !important;
        border-radius: 20px;
    }

    .bookmarks-back-column {
        align-items: flex-start;
    }

    .bookmarks-page-card {
        border-radius: 18px;
        padding: 16px !important;
    }
}


/* ------------------------ Multi-expand bookmarks ------------------------ */

.bookmark-expand-list {
    display: grid;
    gap: 12px;
    margin-top: 14px;
}

.bookmark-expand-card {
    overflow: hidden;
    border: 1px solid rgba(18, 59, 42, 0.09);
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.94);
    box-shadow: 0 10px 24px rgba(18, 59, 42, 0.055);
}

.bookmark-expand-card[open] {
    border-color: rgba(31, 122, 77, 0.22);
    box-shadow: 0 16px 34px rgba(18, 59, 42, 0.08);
}

.bookmark-summary {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    padding: 15px 16px;
    cursor: pointer;
    list-style: none;
}

.bookmark-summary::-webkit-details-marker {
    display: none;
}

.bookmark-summary-main {
    display: grid;
    gap: 4px;
    min-width: 0;
}

.bookmark-summary-title {
    color: var(--gcf-green);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.bookmark-summary-query {
    color: var(--gcf-ink);
    font-size: 15px;
    font-weight: 850;
    line-height: 1.35;
}

.bookmark-summary-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    color: var(--gcf-muted);
    font-size: 12px;
}

.bookmark-summary-meta strong {
    color: var(--gcf-ink);
}

.bookmark-summary-icon {
    display: grid;
    flex: 0 0 auto;
    width: 30px;
    height: 30px;
    place-items: center;
    border-radius: 999px;
    background: var(--gcf-mint-2);
    color: var(--gcf-forest);
    font-weight: 900;
    transition: transform 0.18s ease;
}

.bookmark-expand-card[open] .bookmark-summary-icon {
    transform: rotate(180deg);
}

.bookmark-expand-card .bookmark-detail-card {
    margin: 0 14px 14px;
}


/* --------------------------- Delete bookmark ---------------------------- */

.bookmark-delete-panel {
    margin-bottom: 18px;
    padding: 16px !important;
    border: 1px solid rgba(171, 45, 45, 0.12);
    border-radius: 18px;
    background:
        linear-gradient(145deg, rgba(255,255,255,0.96), rgba(255,247,247,0.92));
}

.bookmark-delete-title {
    color: #7f1d1d;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: -0.01em;
}

.bookmark-delete-subtitle {
    margin: 3px 0 12px;
    color: var(--gcf-muted);
    font-size: 12px;
    line-height: 1.5;
}

#delete-bookmark-choice input,
#delete-bookmark-choice select {
    border-radius: 12px !important;
}

.bookmark-delete-actions {
    justify-content: flex-end;
}

#delete-bookmark-button {
    min-height: 40px !important;
    padding: 0 16px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(185, 28, 28, 0.22) !important;
    background: rgba(255, 255, 255, 0.92) !important;
    color: #991b1b !important;
    font-size: 13px !important;
    font-weight: 900 !important;
    box-shadow: 0 10px 22px rgba(127, 29, 29, 0.08) !important;
}

#delete-bookmark-button:hover {
    transform: translateY(-1px);
    background: #fff5f5 !important;
    box-shadow: 0 14px 28px rgba(127, 29, 29, 0.13) !important;
}

#delete-bookmark-status {
    min-height: 24px;
    color: var(--gcf-muted);
    font-size: 12px;
}


/* ----------------------- Inline bookmark delete button ------------------ */

.bookmark-summary-actions {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    gap: 10px;
}

.bookmark-inline-delete-button {
    min-height: 32px;
    padding: 0 12px;
    border: 1px solid rgba(185, 28, 28, 0.22);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.92);
    color: #991b1b;
    font-size: 12px;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(127, 29, 29, 0.08);
}

.bookmark-inline-delete-button:hover {
    background: #fff5f5;
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(127, 29, 29, 0.13);
}

.bookmark-delete-hidden {
    display: none !important;
}

#delete-bookmark-status {
    min-height: 24px;
    margin-bottom: 10px;
    color: var(--gcf-muted);
    font-size: 12px;
}

@media (max-width: 820px) {
    .bookmark-summary-actions {
        width: 100%;
        justify-content: space-between;
    }

    .bookmark-summary {
        flex-wrap: wrap;
    }
}


/* ---------------------- Real Gradio bookmark delete buttons ------------- */

.bookmark-real-row {
    align-items: stretch;
    gap: 12px !important;
    margin-top: 12px;
}

.bookmark-real-card-column {
    min-width: 0;
}

.bookmark-real-delete-column {
    justify-content: flex-start;
    align-items: flex-end;
    padding-top: 10px;
}

.bookmark-real-delete-button {
    min-height: 36px !important;
    padding: 0 13px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(185, 28, 28, 0.24) !important;
    background: rgba(255, 255, 255, 0.95) !important;
    color: #991b1b !important;
    font-size: 12px !important;
    font-weight: 900 !important;
    box-shadow: 0 8px 18px rgba(127, 29, 29, 0.08) !important;
}

.bookmark-real-delete-button:hover {
    transform: translateY(-1px);
    background: #fff5f5 !important;
    box-shadow: 0 12px 24px rgba(127, 29, 29, 0.13) !important;
}

.bookmark-action-status {
    margin-bottom: 10px;
    padding: 12px 14px;
    border-radius: 14px;
    background: white;
    border: 1px solid rgba(18, 59, 42, 0.08);
    color: var(--gcf-muted);
    font-size: 13px;
    line-height: 1.55;
}

@media (max-width: 820px) {
    .bookmark-real-row {
        gap: 6px !important;
    }

    .bookmark-real-delete-column {
        align-items: flex-start;
        padding-top: 0;
    }
}


/* ----------------------- Pretty recommendation cards -------------------- */

.result-card-heading {
    margin-bottom: 16px;
}

.result-card-kicker {
    display: inline-flex;
    width: fit-content;
    padding: 6px 11px;
    border-radius: 999px;
    background: var(--gcf-mint-2);
    color: var(--gcf-green);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}

.result-card-heading h3 {
    margin: 10px 0 6px;
    color: var(--gcf-ink);
    font-size: 24px;
    font-weight: 900;
    letter-spacing: -0.03em;
}

.result-card-heading p {
    margin: 0;
    color: var(--gcf-muted);
    font-size: 13px;
    line-height: 1.55;
}

.pretty-recommendation-empty {
    padding: 18px 20px;
    border-radius: 18px;
    border: 1px dashed rgba(31, 122, 77, 0.24);
    background: linear-gradient(145deg, rgba(244,251,246,0.95), rgba(255,255,255,0.9));
    color: var(--gcf-muted);
    font-size: 14px;
    line-height: 1.6;
}

.pretty-recommendation-wrapper {
    display: grid;
    gap: 18px;
}

.pretty-recommendation-intro {
    padding: 15px 17px;
    border-radius: 18px;
    border: 1px solid rgba(31, 122, 77, 0.10);
    background:
        linear-gradient(145deg, rgba(244,251,246,0.98), rgba(234,244,251,0.82));
    color: var(--gcf-forest);
    font-size: 14px;
    font-weight: 750;
    line-height: 1.65;
}

.pretty-city-grid {
    display: grid;
    gap: 18px;
}

.pretty-city-card {
    overflow: hidden;
    border-radius: 24px;
    border: 1px solid rgba(18, 59, 42, 0.09);
    background:
        linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,253,251,0.96));
    box-shadow: 0 18px 42px rgba(18, 59, 42, 0.08);
}

.pretty-city-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 20px 22px;
    background:
        radial-gradient(circle at 96% 0%, rgba(31,122,77,0.12), transparent 13rem),
        linear-gradient(135deg, rgba(233,248,239,0.98), rgba(234,244,251,0.88));
    border-bottom: 1px solid rgba(18, 59, 42, 0.07);
}

.pretty-city-rank {
    display: grid;
    width: 44px;
    height: 44px;
    flex: 0 0 auto;
    place-items: center;
    border-radius: 16px;
    background: white;
    color: var(--gcf-green);
    font-size: 18px;
    font-weight: 950;
    box-shadow: 0 10px 22px rgba(18, 59, 42, 0.10);
}

.pretty-city-title {
    color: var(--gcf-ink);
    font-size: 22px;
    font-weight: 950;
    letter-spacing: -0.03em;
    line-height: 1.1;
}

.pretty-city-subtitle {
    margin-top: 4px;
    color: var(--gcf-muted);
    font-size: 12px;
    font-weight: 700;
}

.pretty-city-fields {
    display: grid;
    gap: 12px;
    padding: 18px;
}

.pretty-recommendation-field {
    padding: 14px 15px;
    border-radius: 18px;
    border: 1px solid rgba(18, 59, 42, 0.065);
    background: rgba(247, 251, 248, 0.86);
}

.pretty-recommendation-field-title {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 7px;
    color: var(--gcf-green);
    font-size: 13px;
    letter-spacing: 0.01em;
}

.pretty-field-icon {
    display: grid;
    width: 28px;
    height: 28px;
    place-items: center;
    border-radius: 999px;
    background: white;
    box-shadow: 0 6px 14px rgba(18, 59, 42, 0.06);
}

.pretty-carbon-badge {
    margin-left: auto;
    padding: 4px 9px;
    border-radius: 999px;
    background: #e9f8ef;
    color: var(--gcf-forest);
    font-size: 11px;
    font-weight: 900;
}

.pretty-recommendation-field-body {
    color: var(--gcf-ink);
    font-size: 14px;
    line-height: 1.68;
}

.bookmark-result-pretty {
    padding: 0 !important;
    background: transparent !important;
}

.bookmark-result-pretty .pretty-recommendation-wrapper {
    margin-top: 8px;
}

.bookmark-result-pretty .pretty-city-card {
    box-shadow: none;
}

.search-button-group {
    margin-top: 10px;
}

@media (max-width: 820px) {
    .pretty-city-header {
        align-items: flex-start;
        padding: 17px;
    }

    .pretty-city-rank {
        width: 38px;
        height: 38px;
        border-radius: 14px;
    }

    .pretty-city-title {
        font-size: 19px;
    }

    .pretty-city-fields {
        padding: 14px;
    }

    .pretty-carbon-badge {
        margin-left: 0;
    }
}


/* --------------------------- Markdown output ---------------------------- */

#markdown-recommendation-output {
    padding: 18px 20px !important;
    border-radius: 20px;
    border: 1px solid rgba(18, 59, 42, 0.09);
    background: rgba(255, 255, 255, 0.96);
    box-shadow: 0 12px 28px rgba(18, 59, 42, 0.06);
}

#markdown-recommendation-output h1,
#markdown-recommendation-output h2,
#markdown-recommendation-output h3 {
    color: var(--gcf-ink);
    font-weight: 950;
    letter-spacing: -0.03em;
}

#markdown-recommendation-output p {
    color: var(--gcf-ink);
    font-size: 14px;
    line-height: 1.7;
}

#markdown-recommendation-output strong {
    color: var(--gcf-forest);
    font-weight: 900;
}

#markdown-recommendation-output ul,
#markdown-recommendation-output ol {
    padding-left: 1.4rem;
    color: var(--gcf-ink);
    line-height: 1.7;
}

#markdown-recommendation-output li {
    margin: 7px 0;
}

.bookmark-result-markdown {
    padding: 12px 14px !important;
    border-radius: 16px;
    background: rgba(247, 251, 248, 0.86) !important;
    color: var(--gcf-ink);
}

.bookmark-result-markdown p {
    margin: 8px 0;
    line-height: 1.65;
}

.bookmark-markdown-heading {
    margin: 12px 0 8px;
    color: var(--gcf-ink);
    font-size: 16px;
    font-weight: 900;
}

.bookmark-markdown-list {
    margin: 8px 0 10px;
    padding-left: 1.3rem;
}

.bookmark-markdown-list li {
    margin: 7px 0;
    line-height: 1.65;
}

.search-button-group {
    margin-top: 10px;
}

"""
