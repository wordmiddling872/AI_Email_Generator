from __future__ import annotations

import unittest

from ai_email_generator.models import EmailGenerationInput
from ai_email_generator.parsing import coerce_generated_email


def make_request() -> EmailGenerationInput:
    return EmailGenerationInput(
        template_name="Follow-up",
        tone="Professional",
        length="Medium",
        language="English",
        model="qwen2.5:1.5b",
        temperature=0.65,
        top_p=0.9,
        max_tokens=900,
        recipient_name="Jane Doe",
        sender_name="John Smith",
        purpose="Follow up on the proposal we discussed last week.",
        subject_hint="Follow-up on the proposal",
    )


class ParsingTests(unittest.TestCase):
    def test_parses_json_payload(self) -> None:
        request = make_request()
        result = coerce_generated_email(
            '{"subject":"Proposal follow-up","email":"Dear Jane,\\n\\nThanks for your time.\\n\\nBest,\\nJohn"}',
            request,
            model=request.model,
        )

        self.assertEqual(result.subject, "Proposal follow-up")
        self.assertIn("Dear Jane", result.body)
        self.assertEqual(result.model, request.model)

    def test_parses_plain_text_payload(self) -> None:
        request = make_request()
        result = coerce_generated_email(
            "Subject: Checking in on the proposal\n\nDear Jane,\n\nFollowing up on our discussion.\n\nBest,\nJohn",
            request,
            model=request.model,
        )

        self.assertIn("Checking in on the proposal", result.subject)
        self.assertIn("Dear Jane", result.body)
        self.assertTrue(result.full_text.startswith("Subject: "))


if __name__ == "__main__":
    unittest.main()
