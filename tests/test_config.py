from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from ai_email_generator.config import DEFAULT_MODEL, DEFAULT_OLLAMA_HOST, load_settings


class ConfigTests(unittest.TestCase):
    def test_blank_env_values_fall_back_to_defaults(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_HOST": "   ",
                "OLLAMA_DEFAULT_MODEL": "",
                "EMAILGEN_DEFAULT_LANGUAGE": "   ",
                "EMAILGEN_CLIPBOARD": "",
            },
            clear=False,
        ):
            settings = load_settings()

        self.assertEqual(settings.ollama_host, DEFAULT_OLLAMA_HOST)
        self.assertEqual(settings.default_model, DEFAULT_MODEL)
        self.assertEqual(settings.default_language, "English")
        self.assertTrue(settings.clipboard_enabled)


if __name__ == "__main__":
    unittest.main()
