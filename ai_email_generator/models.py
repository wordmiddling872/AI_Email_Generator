"""Dataclasses used by the AI Email Generator."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class TemplatePreset:
    """Reusable template guidance for a common email scenario."""

    name: str
    description: str
    guidance: str
    default_subject_hint: str = ""
    suggested_cta: str = ""
    example_key_points: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EmailGenerationInput:
    """Normalized user input that will be sent to the LLM."""

    template_name: str
    tone: str
    length: str
    language: str
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    recipient_name: str = ""
    recipient_role: str = ""
    sender_name: str = ""
    sender_role: str = ""
    company_name: str = ""
    subject_hint: str = ""
    purpose: str = ""
    context: str = ""
    key_points: tuple[str, ...] = ()
    desired_outcome: str = ""
    cta: str = ""
    extra_instructions: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EmailGenerationInput":
        raw_key_points = payload.get("key_points", ())
        if isinstance(raw_key_points, list):
            key_points = tuple(str(item) for item in raw_key_points)
        elif isinstance(raw_key_points, tuple):
            key_points = tuple(str(item) for item in raw_key_points)
        else:
            key_points = ()

        return cls(
            template_name=str(payload.get("template_name", "Custom")),
            tone=str(payload.get("tone", "Professional")),
            length=str(payload.get("length", "Medium")),
            language=str(payload.get("language", "English")),
            model=str(payload.get("model", "")),
            temperature=float(payload.get("temperature", 0.65)),
            top_p=float(payload.get("top_p", 0.9)),
            max_tokens=int(payload.get("max_tokens", 900)),
            recipient_name=str(payload.get("recipient_name", "")),
            recipient_role=str(payload.get("recipient_role", "")),
            sender_name=str(payload.get("sender_name", "")),
            sender_role=str(payload.get("sender_role", "")),
            company_name=str(payload.get("company_name", "")),
            subject_hint=str(payload.get("subject_hint", "")),
            purpose=str(payload.get("purpose", "")),
            context=str(payload.get("context", "")),
            key_points=key_points,
            desired_outcome=str(payload.get("desired_outcome", "")),
            cta=str(payload.get("cta", "")),
            extra_instructions=str(payload.get("extra_instructions", "")),
        )


@dataclass(slots=True)
class GeneratedEmail:
    """Structured result returned from the Ollama generation step."""

    subject: str
    body: str
    raw_response: str
    model: str
    template_name: str
    request: EmailGenerationInput = field(repr=False)
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def full_text(self) -> str:
        body = self.body.strip()
        if body:
            return f"Subject: {self.subject.strip()}\n\n{body}"
        return f"Subject: {self.subject.strip()}"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["generated_at"] = self.generated_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GeneratedEmail":
        request_payload = payload.get("request", {})
        if not isinstance(request_payload, dict):
            request_payload = {}
        generated_at = payload.get("generated_at")
        parsed_at = datetime.now(timezone.utc)
        if isinstance(generated_at, str):
            try:
                parsed_at = datetime.fromisoformat(generated_at)
            except ValueError:
                parsed_at = datetime.now(timezone.utc)

        return cls(
            subject=str(payload.get("subject", "")),
            body=str(payload.get("body", "")),
            raw_response=str(payload.get("raw_response", "")),
            model=str(payload.get("model", "")),
            template_name=str(payload.get("template_name", "Custom")),
            request=EmailGenerationInput.from_dict(request_payload),
            generated_at=parsed_at,
        )
