"""Thin Ollama client wrapper used by the app."""

from __future__ import annotations

from ollama import Client

from .config import AppSettings
from .models import EmailGenerationInput, GeneratedEmail
from .parsing import coerce_generated_email
from .prompts import SYSTEM_PROMPT, build_generation_prompt
from .templates import get_template


class EmailGenerationError(RuntimeError):
    """Raised when the model cannot produce a valid response."""


class OllamaUnavailableError(RuntimeError):
    """Raised when the local Ollama server cannot be reached."""


class OllamaEmailService:
    """High-level interface for listing models and generating emails."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self._client = Client(host=settings.ollama_host, timeout=settings.request_timeout_seconds)

    def list_models(self) -> list[str]:
        response = self._client.list()
        models = getattr(response, "models", []) or []
        names: list[str] = []
        for model in models:
            name = getattr(model, "model", "")
            if name:
                names.append(str(name))
        return sorted(dict.fromkeys(names), key=str.lower)

    def health_check(self) -> tuple[bool, str]:
        try:
            response = self._client.list()
            models = getattr(response, "models", []) or []
            count = len(models)
            suffix = "model" if count == 1 else "models"
            return True, f"Ollama is reachable at {self.settings.ollama_host} with {count} {suffix} available."
        except Exception as exc:  # pragma: no cover - depends on local runtime state
            return False, f"Unable to reach Ollama at {self.settings.ollama_host}: {exc}"

    def generate(self, request: EmailGenerationInput) -> GeneratedEmail:
        model_name = request.model.strip() or self.settings.default_model
        if not model_name:
            raise EmailGenerationError("No Ollama model is configured. Enter a model name in the sidebar.")
        prompt = build_generation_prompt(request)

        try:
            response = self._client.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                format="json",
                options={
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "num_predict": request.max_tokens,
                },
            )
        except Exception as exc:  # pragma: no cover - depends on Ollama availability
            raise OllamaUnavailableError(
                f"Failed to contact Ollama at {self.settings.ollama_host}: {exc}"
            ) from exc

        raw_text = getattr(getattr(response, "message", None), "content", "") or ""
        if not raw_text.strip():
            raise EmailGenerationError("Ollama returned an empty response.")

        return coerce_generated_email(raw_text, request, model=model_name)

    def generate_from_prompt(self, prompt: str, *, model: str | None = None) -> str:
        """Legacy helper that keeps the original single-prompt API available."""

        model_name = (model or self.settings.default_model).strip()
        if not model_name:
            raise EmailGenerationError("No Ollama model is configured. Enter a model name in the sidebar.")
        response = self._client.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert business communication assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False,
            options={
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
                "num_predict": self.settings.max_tokens,
            },
        )

        raw_text = getattr(getattr(response, "message", None), "content", "") or ""
        return raw_text.strip()
