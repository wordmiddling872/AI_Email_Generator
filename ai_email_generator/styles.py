"""Custom CSS used by the Streamlit UI."""

from __future__ import annotations


def get_app_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-start: #07111f;
        --bg-end: #0d1a33;
        --surface: rgba(9, 15, 28, 0.78);
        --surface-strong: rgba(13, 20, 36, 0.92);
        --border: rgba(255, 255, 255, 0.10);
        --text: #edf2ff;
        --muted: rgba(237, 242, 255, 0.72);
        --accent: #7dd3fc;
        --accent-2: #34d399;
        --warn: #fbbf24;
        --danger: #fb7185;
    }

    html, body, [class*="css"] {
        font-family: "Manrope", "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(125, 211, 252, 0.16), transparent 28%),
            radial-gradient(circle at right center, rgba(52, 211, 153, 0.14), transparent 24%),
            linear-gradient(180deg, var(--bg-start), var(--bg-end));
        color: var(--text);
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1220px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border: 1px solid var(--border);
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(10, 17, 31, 0.96), rgba(14, 24, 44, 0.92));
        box-shadow: 0 26px 70px rgba(0, 0, 0, 0.28);
        padding: 1.55rem 1.65rem;
        margin-bottom: 1.25rem;
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: auto -8% -45% auto;
        width: 220px;
        height: 220px;
        border-radius: 999px;
        background: radial-gradient(circle, rgba(125, 211, 252, 0.22), transparent 68%);
        pointer-events: none;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.34rem 0.72rem;
        border-radius: 999px;
        background: rgba(125, 211, 252, 0.12);
        border: 1px solid rgba(125, 211, 252, 0.22);
        color: #d8f4ff;
        font-size: 0.76rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-weight: 800;
    }

    .hero h1 {
        margin: 0.75rem 0 0.35rem 0;
        color: var(--text);
        font-size: clamp(2rem, 4vw, 3.35rem);
        line-height: 1.02;
        letter-spacing: -0.04em;
    }

    .hero p {
        margin: 0;
        color: var(--muted);
        max-width: 64ch;
        line-height: 1.6;
    }

    .metric-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .metric-card {
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.04);
        padding: 0.9rem 1rem;
    }

    .metric-label {
        font-size: 0.74rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(237, 242, 255, 0.62);
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--text);
    }

    .metric-note {
        margin-top: 0.25rem;
        color: var(--muted);
        font-size: 0.88rem;
    }

    .glass-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 22px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
        padding: 1rem 1.1rem;
    }

    .section-title {
        margin: 0 0 0.5rem 0;
        color: rgba(237, 242, 255, 0.82);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .small-note {
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        margin: 0.25rem 0.35rem 0.25rem 0;
        padding: 0.32rem 0.65rem;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.10);
        background: rgba(255, 255, 255, 0.05);
        color: rgba(237, 242, 255, 0.92);
        font-size: 0.8rem;
        white-space: nowrap;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .status-ok {
        background: rgba(52, 211, 153, 0.16);
        color: #86efac;
    }

    .status-warn {
        background: rgba(251, 191, 36, 0.16);
        color: #fde68a;
    }

    .status-error {
        background: rgba(251, 113, 133, 0.16);
        color: #fecdd3;
    }

    .output-panel {
        background: var(--surface-strong);
        border: 1px solid rgba(125, 211, 252, 0.24);
        border-radius: 20px;
        padding: 1rem 1.1rem;
    }

    .email-preview {
        white-space: pre-wrap;
        word-break: break-word;
        color: #f3f7ff;
        font-family: "JetBrains Mono", "Consolas", monospace;
        font-size: 0.96rem;
        line-height: 1.7;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.14), transparent);
        margin: 1rem 0;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 2.9rem;
        border-radius: 14px;
        border: 1px solid rgba(125, 211, 252, 0.18);
        background: linear-gradient(135deg, #7dd3fc 0%, #34d399 100%);
        color: #07111f;
        font-weight: 800;
        transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.02);
        box-shadow: 0 10px 24px rgba(52, 211, 153, 0.22);
    }

    .stTextInput input,
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 14px !important;
        color: var(--text) !important;
    }

    .stTextArea textarea {
        min-height: 120px;
    }

    div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 14px !important;
        color: var(--text) !important;
    }

    .stExpander {
        border-color: rgba(255, 255, 255, 0.08) !important;
    }
    </style>
    """
