"""Reusable email templates for common business scenarios."""

from __future__ import annotations

from .models import TemplatePreset


EMAIL_TEMPLATES: dict[str, TemplatePreset] = {
    "Custom": TemplatePreset(
        name="Custom",
        description="A flexible prompt for any email scenario.",
        guidance=(
            "Write a polished email that fits the user's intent. "
            "Prioritize clarity, professionalism, and immediate usability."
        ),
        default_subject_hint="",
        suggested_cta="",
        example_key_points=("Main objective", "Audience", "Any critical details"),
    ),
    "Job Application": TemplatePreset(
        name="Job Application",
        description="Apply for a role with confidence and concise impact.",
        guidance=(
            "Highlight the candidate's strongest relevant skills, achievements, "
            "and enthusiasm for the role. End with a polite request for an interview "
            "or follow-up conversation."
        ),
        default_subject_hint="Application for [Role] at [Company]",
        suggested_cta="I would welcome the opportunity to discuss my application further.",
        example_key_points=("Role title", "Most relevant achievements", "Why this company", "Availability for interview"),
    ),
    "Leave Request": TemplatePreset(
        name="Leave Request",
        description="Request time off in a clear and respectful way.",
        guidance=(
            "State the reason for leave briefly, include the exact dates if provided, "
            "and reassure the recipient that responsibilities will be managed."
        ),
        default_subject_hint="Leave Request for [Dates]",
        suggested_cta="Please let me know if you need any additional details.",
        example_key_points=("Leave dates", "Reason for leave", "Coverage plan", "Any urgency"),
    ),
    "Business Proposal": TemplatePreset(
        name="Business Proposal",
        description="Present an opportunity, value proposition, and next step.",
        guidance=(
            "Frame the proposal around business value, outcomes, and a specific next step. "
            "Keep the language credible, structured, and outcome oriented."
        ),
        default_subject_hint="Business Proposal: [Topic]",
        suggested_cta="I would be glad to schedule a brief discussion at your convenience.",
        example_key_points=("Problem being solved", "Proposed solution", "Business benefit", "Next step"),
    ),
    "Meeting Request": TemplatePreset(
        name="Meeting Request",
        description="Ask for time on someone's calendar with clear context.",
        guidance=(
            "Keep the request concise. Mention why the meeting is needed, suggest a time "
            "or timeframe if available, and make rescheduling easy."
        ),
        default_subject_hint="Meeting Request",
        suggested_cta="Please let me know what time works best for you.",
        example_key_points=("Purpose of the meeting", "Suggested timeframe", "Desired attendees", "Expected outcome"),
    ),
    "Complaint": TemplatePreset(
        name="Complaint",
        description="Escalate an issue professionally without sounding aggressive.",
        guidance=(
            "Describe the issue factually, include the impact, and make a clear ask for a remedy. "
            "Keep the tone firm, calm, and solution focused."
        ),
        default_subject_hint="Issue Regarding [Topic]",
        suggested_cta="I would appreciate your prompt attention to this matter.",
        example_key_points=("What went wrong", "Impact", "Expected resolution", "Relevant dates or references"),
    ),
    "Thank You": TemplatePreset(
        name="Thank You",
        description="Express appreciation in a warm and professional manner.",
        guidance=(
            "Thank the recipient clearly, mention the specific reason for appreciation, "
            "and close with a gracious note."
        ),
        default_subject_hint="Thank You",
        suggested_cta="Thank you again for your support.",
        example_key_points=("What you are thankful for", "Why it mattered", "Any future appreciation or next step"),
    ),
    "Follow-up": TemplatePreset(
        name="Follow-up",
        description="Politely nudge a conversation or previous request.",
        guidance=(
            "Reference the earlier message or conversation, restate the objective, and "
            "make the next step easy to take."
        ),
        default_subject_hint="Follow-up on [Topic]",
        suggested_cta="I look forward to hearing from you soon.",
        example_key_points=("Original message reference", "Current status", "What you need next", "Desired timeline"),
    ),
}

TEMPLATE_NAMES: tuple[str, ...] = tuple(EMAIL_TEMPLATES.keys())

TONE_OPTIONS: tuple[str, ...] = (
    "Professional",
    "Formal",
    "Friendly",
    "Warm",
    "Confident",
    "Persuasive",
)

LENGTH_OPTIONS: tuple[str, ...] = ("Short", "Medium", "Detailed")


def get_template(name: str) -> TemplatePreset:
    """Return a known template or the generic custom template."""

    return EMAIL_TEMPLATES.get(name, EMAIL_TEMPLATES["Custom"])
