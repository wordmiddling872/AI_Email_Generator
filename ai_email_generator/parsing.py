"""Helpers for parsing structured or semi-structured LLM responses."""

from __future__ import annotations

import json
import re
from typing import Any

from .models import EmailGenerationInput, GeneratedEmail

_SUBJECT_RE = re.compile(r"(?im)^\s*subject\s*:\s*(.+?)\s*$")


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def _extract_json_candidate(text: str) -> str:
    stripped = _strip_code_fences(text)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


def _default_subject(request: EmailGenerationInput) -> str:
    if request.subject_hint.strip():
        return request.subject_hint.strip()

    base = request.template_name.strip() or "Email"
    if request.purpose.strip():
        words = request.purpose.strip().split()
        snippet = " ".join(words[:8])
        return f"{base}: {snippet}".strip()
    return base


def _clean_body(body: str) -> str:
    cleaned = _strip_code_fences(body).strip()
    cleaned = re.sub(r"^\s*(email|body)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned


def _extract_subject_and_body_from_text(raw_response: str, request: EmailGenerationInput) -> tuple[str, str]:
    text = _strip_code_fences(raw_response).strip()
    subject_match = _SUBJECT_RE.search(text)
    subject = _default_subject(request)
    body = text

    if subject_match:
        subject = subject_match.group(1).strip()
        body = _SUBJECT_RE.sub("", text, count=1).strip()
        body = re.sub(r"^\s*[-:]+\s*", "", body).strip()

    body = _clean_body(body)
    if not body:
        body = text

    return subject, body


def _parse_payload(payload: dict[str, Any], request: EmailGenerationInput) -> tuple[str, str]:
    subject = str(payload.get("subject", "")).strip() or _default_subject(request)
    body = payload.get("email") or payload.get("body") or payload.get("message") or ""
    body = _clean_body(str(body))
    if not body:
        body = subject
    return subject, body


def coerce_generated_email(
    raw_response: str,
    request: EmailGenerationInput,
    *,
    model: str,
) -> GeneratedEmail:
    """Normalize a raw model response into a structured result."""

    subject = _default_subject(request)
    body = ""

    candidate = _extract_json_candidate(raw_response)
    try:
        payload = json.loads(candidate)
        if isinstance(payload, dict):
            subject, body = _parse_payload(payload, request)
        else:
            subject, body = _extract_subject_and_body_from_text(raw_response, request)
    except Exception:
        subject, body = _extract_subject_and_body_from_text(raw_response, request)

    return GeneratedEmail(
        subject=subject.strip(),
        body=body.strip(),
        raw_response=raw_response.strip(),
        model=model.strip(),
        template_name=request.template_name,
        request=request,
    )
