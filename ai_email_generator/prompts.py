"""Prompt construction for the Ollama chat call."""

from __future__ import annotations

from textwrap import dedent

from .models import EmailGenerationInput
from .templates import get_template


SYSTEM_PROMPT = dedent(
    """
    You are a senior business communication assistant.

    Your job is to write emails that are polished, accurate, and ready to send.
    Follow these rules:
    - Return only a valid JSON object.
    - Use exactly two keys: "subject" and "email".
    - Keep the subject short, specific, and professional.
    - Write the email in the requested language.
    - Include a greeting, body paragraphs, and a closing signature.
    - Do not include markdown fences, notes, or commentary.
    - Do not mention that you are an AI.
    - If the user leaves a detail blank, make a sensible professional assumption.
    """
).strip()


_LENGTH_GUIDANCE = {
    "Short": "Aim for a compact email with one to two short body paragraphs.",
    "Medium": "Aim for a standard business email with two to three body paragraphs.",
    "Detailed": "Aim for a more thorough email with three to five body paragraphs.",
}


def _clean(text: str) -> str:
    return " ".join(text.split()).strip()


def _format_block(label: str, value: str) -> str:
    cleaned = value.strip()
    return f"{label}: {cleaned if cleaned else 'Not provided'}"


def _format_key_points(request: EmailGenerationInput) -> str:
    if request.key_points:
        points = [f"- {point.strip()}" for point in request.key_points if point.strip()]
        if points:
            return "\n".join(points)
    return "- Not provided"


def build_generation_prompt(request: EmailGenerationInput) -> str:
    """Build a structured prompt from the user's form input."""

    template = get_template(request.template_name)

    recipient_line = ", ".join(
        value
        for value in [
            _clean(request.recipient_name),
            _clean(request.recipient_role),
            _clean(request.company_name),
        ]
        if value
    )
    sender_line = ", ".join(
        value
        for value in [
            _clean(request.sender_name),
            _clean(request.sender_role),
        ]
        if value
    )

    subject_hint = _clean(request.subject_hint) or template.default_subject_hint
    cta = _clean(request.cta) or template.suggested_cta

    prompt_parts = [
        "Write a complete business email using the brief below.",
        "",
        _format_block("Email type", request.template_name),
        _format_block("Tone", request.tone),
        _format_block("Length", request.length),
        _format_block("Language", request.language),
        _format_block("Recipient", recipient_line),
        _format_block("Sender", sender_line),
        _format_block("Subject hint", subject_hint),
        _format_block("Purpose", request.purpose),
        _format_block("Context", request.context),
        _format_block("Desired outcome", request.desired_outcome),
        _format_block("Call to action", cta),
        "Key points:",
        _format_key_points(request),
        "",
        "Template guidance:",
        template.guidance,
        "",
        _LENGTH_GUIDANCE.get(request.length, _LENGTH_GUIDANCE["Medium"]),
        "",
        "Extra instructions:",
        request.extra_instructions.strip() or "None provided",
        "",
        "Output requirements:",
        '- Return valid JSON only using this schema: {"subject": "...", "email": "..."}',
        "- The email value must be a fully written email with greeting, body, and closing.",
        "- Keep the subject concise and specific.",
        "- Use natural paragraph breaks and avoid filler language.",
        "- Do not add commentary outside the JSON object.",
    ]

    return "\n".join(prompt_parts).strip()
