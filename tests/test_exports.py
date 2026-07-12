from __future__ import annotations

import unittest

from ai_email_generator.exports import export_email_docx, export_email_pdf, export_email_txt, safe_filename
from ai_email_generator.models import EmailGenerationInput, GeneratedEmail


def make_email() -> GeneratedEmail:
    request = EmailGenerationInput(
        template_name="Thank You",
        tone="Warm",
        length="Short",
        language="English",
        model="qwen2.5:1.5b",
        temperature=0.65,
        top_p=0.9,
        max_tokens=900,
        sender_name="John Smith",
        purpose="Say thank you for the meeting.",
    )
    return GeneratedEmail(
        subject="Thank You for Your Time",
        body="Dear Jane,\n\nThank you again for meeting with me.\n\nBest regards,\nJohn",
        raw_response='{"subject":"Thank You for Your Time","email":"..."}',
        model=request.model,
        template_name=request.template_name,
        request=request,
    )


class ExportTests(unittest.TestCase):
    def test_safe_filename(self) -> None:
        self.assertEqual(safe_filename("Hello, World!"), "hello_world.txt")

    def test_txt_export_contains_subject(self) -> None:
        email = make_email()
        payload = export_email_txt(email).decode("utf-8")
        self.assertIn("Subject: Thank You for Your Time", payload)

    def test_docx_and_pdf_exports_return_bytes(self) -> None:
        email = make_email()
        docx_bytes = export_email_docx(email)
        pdf_bytes = export_email_pdf(email)
        self.assertTrue(docx_bytes.startswith(b"PK"))
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
