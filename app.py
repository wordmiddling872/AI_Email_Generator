"""Streamlit front-end for the AI Email Generator."""

from __future__ import annotations

from dataclasses import replace
from html import escape
import re
import time
from typing import Iterable

import streamlit as st

try:  # Optional, but available in the local environment.
    import pyperclip
except Exception:  # pragma: no cover - clipboard support depends on host OS
    pyperclip = None

from ai_email_generator.config import AppSettings, load_settings
from ai_email_generator.exports import (
    export_email_docx,
    export_email_md,
    export_email_pdf,
    export_email_txt,
    safe_filename,
)
from ai_email_generator.models import EmailGenerationInput, GeneratedEmail
from ai_email_generator.ollama_service import (
    EmailGenerationError,
    OllamaEmailService,
    OllamaUnavailableError,
)
from ai_email_generator.prompts import build_generation_prompt
from ai_email_generator.styles import get_app_css
from ai_email_generator.templates import LENGTH_OPTIONS, TEMPLATE_NAMES, TONE_OPTIONS, get_template


APP_TITLE = "AI Email Generator"
APP_ICON = "📧"


@st.cache_resource(show_spinner=False)
def get_service(settings: AppSettings) -> OllamaEmailService:
    return OllamaEmailService(settings)


@st.cache_data(ttl=25, show_spinner=False)
def get_connection_status(ollama_host: str, refresh_nonce: int) -> tuple[bool, str]:
    service = OllamaEmailService(AppSettings(ollama_host=ollama_host))
    return service.health_check()


@st.cache_data(ttl=25, show_spinner=False)
def get_model_names(ollama_host: str, refresh_nonce: int) -> tuple[str, ...]:
    service = OllamaEmailService(AppSettings(ollama_host=ollama_host))
    try:
        return tuple(service.list_models())
    except Exception:
        return tuple()


def init_state() -> None:
    defaults = {
        "generation_history": [],
        "generated_subject": "",
        "generated_body": "",
        "generated_raw": "",
        "last_generated": None,
        "latest_prompt": "",
        "last_generation_seconds": 0.0,
        "model_refresh_nonce": 0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def trim_history(limit: int) -> None:
    history = list(st.session_state.get("generation_history", []))
    if len(history) > limit:
        st.session_state["generation_history"] = history[:limit]


def format_timestamp(value: object) -> str:
    if hasattr(value, "astimezone"):
        try:
            return value.astimezone().strftime("%B %d, %Y at %I:%M %p %Z")
        except Exception:
            pass
    return "Just now"


def parse_key_points(raw_text: str) -> tuple[str, ...]:
    text = raw_text.strip()
    if not text:
        return tuple()

    candidates = re.split(r"[\n\r;]+", text)
    if len(candidates) == 1 and "," in text:
        candidates = [part.strip() for part in text.split(",")]

    cleaned: list[str] = []
    for candidate in candidates:
        item = candidate.strip().lstrip("-*•").strip()
        if item:
            cleaned.append(item)
    return tuple(cleaned)


def status_badge(ok: bool, label: str) -> str:
    pill_class = "status-ok" if ok else "status-error"
    return f"<span class='status-pill {pill_class}'>{escape(label)}</span>"


def chips_html(values: Iterable[str]) -> str:
    chips = [f"<span class='chip'>{escape(value)}</span>" for value in values if value]
    return "".join(chips)


def render_hero(settings: AppSettings, model_names: tuple[str, ...], health_ok: bool) -> None:
    history_count = len(st.session_state.get("generation_history", []))
    model_count = len(model_names)
    model_label = settings.default_model or "No model selected"
    health_label = "Connected" if health_ok else "Check Ollama"

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">Local AI writing studio</div>
            <h1>AI Email Generator</h1>
            <p>
                Build polished business emails with Ollama on your own machine.
                Draft, edit, export, and keep everything private by design.
            </p>
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-label">Connection</div>
                    <div class="metric-value">{escape(health_label)}</div>
                    <div class="metric-note">{escape(settings.ollama_host)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Model</div>
                    <div class="metric-value">{escape(model_label)}</div>
                    <div class="metric-note">{model_count} installed model(s) detected</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Workspace</div>
                    <div class="metric-value">{history_count} saved draft(s)</div>
                    <div class="metric-note">TXT, MD, DOCX, and PDF export</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(base_settings: AppSettings) -> tuple[AppSettings, tuple[str, ...], bool, str]:
    st.sidebar.markdown("## Controls")
    st.sidebar.caption("These settings shape the local Ollama client and generation behavior.")

    ollama_host = st.sidebar.text_input("Ollama host", value=base_settings.ollama_host)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.5, value=base_settings.temperature, step=0.05)
    top_p = st.sidebar.slider("Top-p", 0.1, 1.0, value=base_settings.top_p, step=0.05)
    max_tokens = st.sidebar.slider("Max tokens", 128, 2048, value=base_settings.max_tokens, step=32)
    history_limit = st.sidebar.slider("History limit", 1, 50, value=base_settings.history_limit, step=1)
    clipboard_enabled = st.sidebar.checkbox("Enable clipboard copy", value=base_settings.clipboard_enabled)

    if st.sidebar.button("Refresh model list", use_container_width=True):
        st.session_state["model_refresh_nonce"] = int(st.session_state.get("model_refresh_nonce", 0)) + 1
        st.rerun()

    refresh_nonce = int(st.session_state.get("model_refresh_nonce", 0))
    normalized_host = str(ollama_host).strip().rstrip("/") or base_settings.ollama_host
    connected, message = get_connection_status(normalized_host, refresh_nonce)
    models = get_model_names(normalized_host, refresh_nonce)

    if models:
        default_model = base_settings.default_model if base_settings.default_model in models else models[0]
        selected_model = st.sidebar.selectbox(
            "Installed model",
            options=models,
            index=models.index(default_model),
            help="Pick one of the models already installed in Ollama.",
        )
        custom_model = st.sidebar.text_input(
            "Custom model override",
            value="",
            placeholder="Optional: type a model tag if you want to use one not listed above.",
        )
        model_name = custom_model.strip() or selected_model
    else:
        st.sidebar.info("No installed models were detected. Type a model name manually or pull one with Ollama.")
        model_name = st.sidebar.text_input("Model", value=base_settings.default_model)

    settings = AppSettings(
        ollama_host=normalized_host,
        default_model=str(model_name).strip() or (
            base_settings.default_model if base_settings.default_model.strip() else "qwen2.5:1.5b"
        ),
        temperature=float(temperature),
        top_p=float(top_p),
        max_tokens=int(max_tokens),
        request_timeout_seconds=base_settings.request_timeout_seconds,
        history_limit=int(history_limit),
        default_language=base_settings.default_language,
        clipboard_enabled=bool(clipboard_enabled),
    )

    st.sidebar.markdown("### Ollama status")
    st.sidebar.markdown(
        f"""
        <div class="glass-card">
            {status_badge(connected, "Online" if connected else "Offline")}
            <div class="small-note" style="margin-top: 0.55rem;">{escape(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Installed models")
    if models:
        st.sidebar.markdown(f"<div>{chips_html(models)}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.warning("No models detected yet. Pull one with `ollama pull <model>`.")

    st.sidebar.markdown("### Tips")
    st.sidebar.caption(
        "Use short prompts for fast drafts and a more specific model for higher quality business writing."
    )

    return settings, models, connected, message


def build_request(
    *,
    template_name: str,
    tone: str,
    length: str,
    language: str,
    recipient_name: str,
    recipient_role: str,
    sender_name: str,
    sender_role: str,
    company_name: str,
    subject_hint: str,
    purpose: str,
    context: str,
    key_points: tuple[str, ...],
    desired_outcome: str,
    cta: str,
    extra_instructions: str,
    settings: AppSettings,
) -> EmailGenerationInput:
    return EmailGenerationInput(
        template_name=template_name,
        tone=tone,
        length=length,
        language=language.strip() or settings.default_language,
        model=settings.default_model,
        temperature=settings.temperature,
        top_p=settings.top_p,
        max_tokens=settings.max_tokens,
        recipient_name=recipient_name.strip(),
        recipient_role=recipient_role.strip(),
        sender_name=sender_name.strip(),
        sender_role=sender_role.strip(),
        company_name=company_name.strip(),
        subject_hint=subject_hint.strip(),
        purpose=purpose.strip(),
        context=context.strip(),
        key_points=key_points,
        desired_outcome=desired_outcome.strip(),
        cta=cta.strip(),
        extra_instructions=extra_instructions.strip(),
    )


def store_generation(result: GeneratedEmail, prompt: str, history_limit: int) -> None:
    st.session_state["generated_subject"] = result.subject
    st.session_state["generated_body"] = result.body
    st.session_state["generated_raw"] = result.raw_response
    st.session_state["last_generated"] = result.to_dict()
    st.session_state["latest_prompt"] = prompt

    history = list(st.session_state.get("generation_history", []))
    history.insert(0, result.to_dict())
    st.session_state["generation_history"] = history[:history_limit]


def clear_current_editor() -> None:
    st.session_state["generated_subject"] = ""
    st.session_state["generated_body"] = ""
    st.session_state["generated_raw"] = ""
    st.session_state["last_generated"] = None
    st.session_state["latest_prompt"] = ""
    st.session_state["last_generation_seconds"] = 0.0


def load_draft_into_editor(serialized_email: dict[str, object]) -> None:
    """Load a saved draft into the editor state before widgets are rebuilt."""

    st.session_state["generated_subject"] = str(serialized_email.get("subject", ""))
    st.session_state["generated_body"] = str(serialized_email.get("body", ""))
    st.session_state["generated_raw"] = str(serialized_email.get("raw_response", ""))
    st.session_state["last_generated"] = serialized_email
    st.session_state["latest_prompt"] = build_generation_prompt(
        GeneratedEmail.from_dict(serialized_email).request
    )
    st.session_state["last_generation_seconds"] = 0.0


def copy_to_clipboard(text: str) -> tuple[bool, str]:
    if pyperclip is None:
        return False, "Clipboard support is unavailable in this environment."

    try:
        pyperclip.copy(text)
        return True, "Copied to clipboard."
    except Exception as exc:  # pragma: no cover - depends on local host clipboard
        return False, str(exc)


def render_template_summary(template_name: str) -> None:
    template = get_template(template_name)
    example_points = template.example_key_points[:4]
    subject_hint = template.default_subject_hint or "No default subject hint"
    cta = template.suggested_cta or "No default call to action"

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">Template brief</div>
            <div class="small-note">{escape(template.description)}</div>
            <div class="divider"></div>
            <div class="small-note"><strong>Suggested subject:</strong> {escape(subject_hint)}</div>
            <div class="small-note" style="margin-top: 0.35rem;"><strong>Suggested CTA:</strong> {escape(cta)}</div>
            <div style="margin-top: 0.55rem;">{chips_html(example_points)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_panel(settings: AppSettings) -> None:
    payload = st.session_state.get("last_generated")
    if not payload:
        st.info("Generate an email to see the editable result, exports, and raw response here.")
        return

    result = GeneratedEmail.from_dict(payload)
    subject_value = st.text_input("Subject", key="generated_subject")
    body_value = st.text_area("Email body", key="generated_body", height=320)
    display_email = replace(result, subject=subject_value.strip() or result.subject, body=body_value.strip() or result.body)

    prompt = st.session_state.get("latest_prompt", "")
    duration = float(st.session_state.get("last_generation_seconds", 0.0))

    st.markdown(
        f"""
        <div class="output-panel">
            <div class="section-title">Live preview</div>
            <div class="email-preview">{escape(display_email.full_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if duration > 0:
        st.caption(
            f"Generated with `{display_email.model}` in {duration:.2f}s on {format_timestamp(display_email.generated_at)}."
        )
    else:
        st.caption(f"Loaded from history on {format_timestamp(display_email.generated_at)}.")

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Copy to clipboard", use_container_width=True, disabled=not settings.clipboard_enabled):
            ok, message = copy_to_clipboard(display_email.full_text)
            if ok:
                st.toast(message)
            else:
                st.warning(message)
    with action_col2:
        st.button("Clear editor", use_container_width=True, on_click=clear_current_editor)

    download_col1, download_col2, download_col3, download_col4 = st.columns(4)
    with download_col1:
        st.download_button(
            "TXT",
            data=export_email_txt(display_email),
            file_name=safe_filename(display_email.subject, suffix="txt"),
            mime="text/plain",
            use_container_width=True,
        )
    with download_col2:
        st.download_button(
            "Markdown",
            data=export_email_md(display_email),
            file_name=safe_filename(display_email.subject, suffix="md"),
            mime="text/markdown",
            use_container_width=True,
        )
    with download_col3:
        st.download_button(
            "DOCX",
            data=export_email_docx(display_email),
            file_name=safe_filename(display_email.subject, suffix="docx"),
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with download_col4:
        st.download_button(
            "PDF",
            data=export_email_pdf(display_email),
            file_name=safe_filename(display_email.subject, suffix="pdf"),
            mime="application/pdf",
            use_container_width=True,
        )

    with st.expander("Show raw model output and prompt", expanded=False):
        st.code(result.raw_response, language="json")
        if prompt:
            st.code(prompt, language="text")


def render_compose_tab(settings: AppSettings, models: tuple[str, ...], connected: bool) -> None:
    template_name = st.selectbox("Email template", TEMPLATE_NAMES, index=0)
    render_template_summary(template_name)

    if not connected:
        st.warning("Ollama is currently offline. The form is ready, but generation will fail until the server is reachable.")

    with st.form("email_builder", clear_on_submit=False):
        left_col, right_col = st.columns(2)

        with left_col:
            recipient_name = st.text_input("Recipient name", placeholder="Priya Sharma")
            recipient_role = st.text_input("Recipient role", placeholder="Hiring Manager")
            sender_name = st.text_input("Your name", placeholder="Arjun Mehta")
            sender_role = st.text_input("Your role", placeholder="Product Designer")

        with right_col:
            company_name = st.text_input("Company", placeholder="Acme Labs")
            language = st.text_input("Language", value=settings.default_language, help="Any language your Ollama model can write in.")
            tone = st.selectbox("Tone", TONE_OPTIONS, index=0)
            length = st.selectbox("Length", LENGTH_OPTIONS, index=1)

        purpose = st.text_area(
            "Purpose",
            height=140,
            placeholder="What should this email achieve?",
        )
        context = st.text_area(
            "Context",
            height=120,
            placeholder="Add dates, background, constraints, or conversation history.",
        )

        key_points_text = st.text_area(
            "Key points",
            height=110,
            placeholder="One point per line or a comma-separated list.",
        )

        secondary_col1, secondary_col2 = st.columns(2)
        with secondary_col1:
            subject_hint = st.text_input(
                "Subject hint",
                placeholder=get_template(template_name).default_subject_hint or "Optional subject line hint",
            )
        with secondary_col2:
            desired_outcome = st.text_input(
                "Desired outcome",
                placeholder="e.g. schedule a meeting or request approval",
            )

        cta = st.text_input(
            "Call to action",
            placeholder=get_template(template_name).suggested_cta or "Optional closing request",
        )

        extra_instructions = st.text_area(
            "Extra instructions",
            height=90,
            placeholder="Add any style, compliance, or formatting requirements.",
        )

        advanced = st.expander("Advanced generation settings", expanded=False)
        with advanced:
            st.write(
                "The core generation controls live in the sidebar. If you need more models, pull them locally with `ollama pull <model>`."
            )
            st.markdown(
                f"""
                <div class="small-note">
                    <strong>Installed models:</strong><br/>
                    {chips_html(models if models else (settings.default_model,))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        submitted = st.form_submit_button("Generate email")

    if submitted:
        if not purpose.strip():
            st.error("Please describe the email purpose before generating.")
            return

        request = build_request(
            template_name=template_name,
            tone=tone,
            length=length,
            language=language,
            recipient_name=recipient_name,
            recipient_role=recipient_role,
            sender_name=sender_name,
            sender_role=sender_role,
            company_name=company_name,
            subject_hint=subject_hint,
            purpose=purpose,
            context=context,
            key_points=parse_key_points(key_points_text),
            desired_outcome=desired_outcome,
            cta=cta,
            extra_instructions=extra_instructions,
            settings=settings,
        )

        prompt = build_generation_prompt(request)
        service = get_service(settings)
        started_at = time.perf_counter()

        try:
            with st.spinner("Generating the email locally with Ollama..."):
                result = service.generate(request)
        except OllamaUnavailableError as exc:
            st.error(str(exc))
            return
        except EmailGenerationError as exc:
            st.error(str(exc))
            return
        except Exception as exc:  # pragma: no cover - defensive runtime fallback
            st.exception(exc)
            return

        duration = time.perf_counter() - started_at
        st.session_state["last_generation_seconds"] = duration
        store_generation(result, prompt, settings.history_limit)
        st.toast("Email generated successfully.")
        st.success(f"Generated in {duration:.2f}s with {result.model}.")

    render_result_panel(settings)


def render_history_tab(settings: AppSettings) -> None:
    history = [GeneratedEmail.from_dict(item) for item in st.session_state.get("generation_history", [])]
    if not history:
        st.info("No saved drafts yet. Generate an email and it will appear here.")
        return

    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.subheader(f"Saved drafts ({len(history)})")
    with header_col2:
        if st.button("Clear history", use_container_width=True):
            st.session_state["generation_history"] = []
            st.rerun()

    for index, item in enumerate(history):
        with st.expander(f"{index + 1}. {item.subject}", expanded=index == 0):
            meta_cols = st.columns(4)
            with meta_cols[0]:
                st.markdown(f"<div class='chip'>{escape(item.template_name)}</div>", unsafe_allow_html=True)
            with meta_cols[1]:
                st.markdown(f"<div class='chip'>{escape(item.model)}</div>", unsafe_allow_html=True)
            with meta_cols[2]:
                st.markdown(f"<div class='chip'>{escape(format_timestamp(item.generated_at))}</div>", unsafe_allow_html=True)
            with meta_cols[3]:
                st.markdown(f"<div class='chip'>{escape(item.request.tone)}</div>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="output-panel">
                    <div class="section-title">Draft preview</div>
                    <div class="email-preview">{escape(item.full_text)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            action_cols = st.columns(3)
            with action_cols[0]:
                st.button(
                    "Load into editor",
                    key=f"load_{index}",
                    use_container_width=True,
                    on_click=load_draft_into_editor,
                    args=(item.to_dict(),),
                )
            with action_cols[1]:
                st.download_button(
                    "TXT",
                    data=export_email_txt(item),
                    file_name=safe_filename(item.subject, suffix="txt"),
                    mime="text/plain",
                    key=f"history_txt_{index}",
                    use_container_width=True,
                )
            with action_cols[2]:
                st.download_button(
                    "PDF",
                    data=export_email_pdf(item),
                    file_name=safe_filename(item.subject, suffix="pdf"),
                    mime="application/pdf",
                    key=f"history_pdf_{index}",
                    use_container_width=True,
                )


def render_setup_tab(settings: AppSettings, model_names: tuple[str, ...], health_ok: bool, health_message: str) -> None:
    st.subheader("Quick start")
    st.markdown(
        """
        1. Install Ollama from the official site.
        2. Pull a model, for example `ollama pull qwen2.5:1.5b`.
        3. Install the Python requirements.
        4. Launch the app with `streamlit run app.py`.
        """
    )

    st.code(
        "\n".join(
            [
                "ollama pull qwen2.5:1.5b",
                "python -m pip install -r requirements.txt",
                "streamlit run app.py",
            ]
        ),
        language="bash",
    )

    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Current runtime</div>
                <div class="small-note"><strong>Host:</strong> {escape(settings.ollama_host)}</div>
                <div class="small-note"><strong>Model:</strong> {escape(settings.default_model)}</div>
                <div class="small-note"><strong>Clipboard:</strong> {'Enabled' if settings.clipboard_enabled else 'Disabled'}</div>
                <div class="small-note"><strong>History limit:</strong> {settings.history_limit}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with info_col2:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Connection</div>
                {status_badge(health_ok, "Online" if health_ok else "Offline")}
                <div class="small-note" style="margin-top: 0.55rem;">{escape(health_message)}</div>
                <div class="small-note" style="margin-top: 0.55rem;"><strong>Detected models:</strong> {len(model_names)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Environment variables")
    st.code(
        "\n".join(
            [
                "OLLAMA_HOST=http://localhost:11434",
                "OLLAMA_DEFAULT_MODEL=qwen2.5:1.5b",
                "EMAILGEN_TEMPERATURE=0.65",
                "EMAILGEN_TOP_P=0.9",
                "EMAILGEN_MAX_TOKENS=900",
                "EMAILGEN_HISTORY_LIMIT=12",
                "EMAILGEN_DEFAULT_LANGUAGE=English",
                "EMAILGEN_CLIPBOARD=true",
            ]
        ),
        language="dotenv",
    )

    st.subheader("Architecture")
    st.markdown(
        """
        - `app.py` owns the Streamlit layout and state.
        - `ai_email_generator/ollama_service.py` isolates the Ollama client.
        - `ai_email_generator/prompts.py` builds structured prompts.
        - `ai_email_generator/parsing.py` normalizes model output.
        - `ai_email_generator/exports.py` produces TXT, MD, DOCX, and PDF downloads.
        """
    )

    st.subheader("Troubleshooting")
    st.markdown(
        """
        - If the model list is empty, make sure the Ollama server is running.
        - If generation fails, verify the model name exactly matches an installed Ollama tag.
        - If clipboard copy fails, the OS clipboard backend may be unavailable in the current session.
        """
    )


def main() -> None:
    settings = load_settings()
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")
    init_state()
    st.markdown(get_app_css(), unsafe_allow_html=True)

    current_settings, model_names, health_ok, health_message = render_sidebar(settings)
    trim_history(current_settings.history_limit)
    render_hero(current_settings, model_names, health_ok)

    tabs = st.tabs(["Compose", "History", "Setup"])
    with tabs[0]:
        render_compose_tab(current_settings, model_names, health_ok)
    with tabs[1]:
        render_history_tab(current_settings)
    with tabs[2]:
        render_setup_tab(current_settings, model_names, health_ok, health_message)


if __name__ == "__main__":
    main()
