"""Application configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Final

try:  # Optional runtime dependency; the app should still start without a .env file.
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - import-time fallback
    def load_dotenv(*args: object, **kwargs: object) -> bool:  # type: ignore[override]
        return False


DEFAULT_OLLAMA_HOST: Final[str] = "http://localhost:11434"
DEFAULT_MODEL: Final[str] = "qwen2.5:1.5b"


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Static app-level defaults loaded from environment variables."""

    ollama_host: str = DEFAULT_OLLAMA_HOST
    default_model: str = DEFAULT_MODEL
    temperature: float = 0.65
    top_p: float = 0.9
    max_tokens: int = 900
    request_timeout_seconds: int = 120
    history_limit: int = 12
    default_language: str = "English"
    clipboard_enabled: bool = True


def _float_env(name: str, fallback: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return fallback
    try:
        return float(raw)
    except ValueError:
        return fallback


def _str_env(name: str, fallback: str) -> str:
    raw = os.getenv(name)
    if raw is None:
        return fallback

    cleaned = raw.strip()
    return cleaned or fallback


def _bool_env(name: str, fallback: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return fallback

    cleaned = raw.strip().lower()
    if not cleaned:
        return fallback
    return cleaned not in {"0", "false", "no", "off"}


def _int_env(name: str, fallback: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return fallback
    try:
        return int(raw)
    except ValueError:
        return fallback


def load_settings() -> AppSettings:
    """Load settings from the environment and an optional .env file."""

    load_dotenv()

    return AppSettings(
        ollama_host=_str_env("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/"),
        default_model=_str_env("OLLAMA_DEFAULT_MODEL", DEFAULT_MODEL),
        temperature=_float_env("EMAILGEN_TEMPERATURE", 0.65),
        top_p=_float_env("EMAILGEN_TOP_P", 0.9),
        max_tokens=_int_env("EMAILGEN_MAX_TOKENS", 900),
        request_timeout_seconds=_int_env("EMAILGEN_TIMEOUT", 120),
        history_limit=_int_env("EMAILGEN_HISTORY_LIMIT", 12),
        default_language=_str_env("EMAILGEN_DEFAULT_LANGUAGE", "English"),
        clipboard_enabled=_bool_env("EMAILGEN_CLIPBOARD", True),
    )
