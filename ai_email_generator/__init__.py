"""AI Email Generator package."""

from .config import AppSettings, load_settings
from .exports import (
    export_email_docx,
    export_email_md,
    export_email_pdf,
    export_email_txt,
    safe_filename,
)
from .models import EmailGenerationInput, GeneratedEmail, TemplatePreset
from .ollama_service import EmailGenerationError, OllamaEmailService, OllamaUnavailableError
from .prompts import SYSTEM_PROMPT, build_generation_prompt

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "AppSettings",
    "EmailGenerationError",
    "EmailGenerationInput",
    "GeneratedEmail",
    "OllamaEmailService",
    "OllamaUnavailableError",
    "SYSTEM_PROMPT",
    "TemplatePreset",
    "build_generation_prompt",
    "export_email_docx",
    "export_email_md",
    "export_email_pdf",
    "export_email_txt",
    "load_settings",
    "safe_filename",
]
