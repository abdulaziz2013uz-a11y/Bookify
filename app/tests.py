import json
import os
from unittest.mock import patch

from django.test import TestCase, override_settings

from .models import Book


@override_settings(ALLOWED_HOSTS=["testserver"], SECURE_SSL_REDIRECT=False)
class AIChatTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="O'tkan kunlar",
            author="Abdulla Qodiriy",
            genre="Tarixiy roman",
            price="25000",
            description="O'zbek adabiyotining mashhur romani.",
            published_date="1925-01-01",
        )

    def test_public_books_page_shows_chat_widget(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bookify AI")
        self.assertContains(response, "csrfmiddlewaretoken")

    @patch.dict(os.environ, {}, clear=False)
    def test_chat_returns_catalog_recommendation_without_api_key(self):
        os.environ.pop("GROQ_API_KEY", None)
        os.environ.pop("GEMINI_API_KEY", None)
        response = self.client.post(
            "/ai/chat/",
            data=json.dumps({"message": "tarixiy roman tavsiya qil"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.book.title, response.json()["answer"])
        self.assertIn("AI API kaliti ulanmagan", response.json()["answer"])

    def test_chat_rejects_empty_and_oversized_messages(self):
        empty_response = self.client.post(
            "/ai/chat/",
            data=json.dumps({"message": "  "}),
            content_type="application/json",
        )
        oversized_response = self.client.post(
            "/ai/chat/",
            data=json.dumps({"message": "a" * 1001}),
            content_type="application/json",
        )

        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(oversized_response.status_code, 400)

    @patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "test-key", "GROQ_API_KEY": "test-groq-key"},
    )
    @patch("app.ai_assistant.urlopen")
    def test_chat_uses_gemini_when_api_key_is_configured(self, mock_urlopen):
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.read.return_value = json.dumps(
            {
                "candidates": [
                    {"content": {"parts": [{"text": "Mana sizga kitob tavsiyasi."}]}}
                ]
            }
        ).encode("utf-8")
        mock_urlopen.return_value = mock_response

        response = self.client.post(
            "/ai/chat/",
            data=json.dumps({"message": "Tarixiy kitob tavsiya qil"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Mana sizga kitob tavsiyasi.")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.5-flash:generateContent",
        )
        self.assertEqual(request.get_header("X-goog-api-key"), "test-key")

    @patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "test-openrouter-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "GROQ_API_KEY": "test-groq-key",
        },
    )
    @patch("app.ai_assistant.urlopen")
    def test_chat_uses_openrouter_when_api_key_is_configured(self, mock_urlopen):
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "OpenRouter tavsiyasi."}}]}
        ).encode("utf-8")
        mock_urlopen.return_value = mock_response

        response = self.client.post(
            "/ai/chat/",
            data=json.dumps({"message": "Tarixiy kitob tavsiya qil"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "OpenRouter tavsiyasi.")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://openrouter.ai/api/v1/chat/completions",
        )
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer test-openrouter-key",
        )
        self.assertEqual(
            json.loads(request.data)["model"],
            "openrouter/free",
        )

    @patch.dict(os.environ, {"GROQ_API_KEY": "test-groq-key"}, clear=False)
    @patch("app.ai_assistant.urlopen")
    def test_chat_uses_groq_when_groq_api_key_is_configured(self, mock_urlopen):
        from unittest.mock import MagicMock

        os.environ.pop("GEMINI_API_KEY", None)
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.read.return_value = json.dumps(
            {
                "choices": [
                    {"message": {"content": "Mana Groq AI tavsiyasi."}}
                ]
            }
        ).encode("utf-8")
        mock_urlopen.return_value = mock_response

        response = self.client.post(
            "/ai/chat/",
            data=json.dumps({"message": "Fantastik kitob tavsiya qil"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Mana Groq AI tavsiyasi.")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://api.groq.com/openai/v1/chat/completions",
        )
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer test-groq-key",
        )
