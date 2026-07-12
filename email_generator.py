"""Backward-compatible single-function wrapper for the legacy API."""

from __future__ import annotations

from ollama import Client

from ai_email_generator.config import load_settings

LEGACY_SYSTEM_PROMPT = """
You are an expert business communication assistant.

Rules:
1. Generate a professional subject.
2. Write grammatically correct emails.
3. Use a proper greeting.
4. Use a proper closing.
5. Use paragraphs.
6. Never explain.
7. Return only the email.
""".strip()


def generate_email(prompt: str, model: str | None = None) -> str:
    """Preserve the original prompt-in, text-out interface."""

    settings = load_settings()
    model_name = (model or settings.default_model).strip()
    if not model_name:
        raise RuntimeError("No Ollama model is configured. Set OLLAMA_DEFAULT_MODEL or enter a model in the app.")
    client = Client(host=settings.ollama_host, timeout=settings.request_timeout_seconds)

    response = client.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": LEGACY_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=False,
        options={
            "temperature": settings.temperature,
            "top_p": settings.top_p,
            "num_predict": settings.max_tokens,
        },
    )

    content = getattr(getattr(response, "message", None), "content", "") or ""
    return content.strip()
