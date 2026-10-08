import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.db.models import Avg

from .models import Book

logger = logging.getLogger(__name__)


class AssistantUnavailable(Exception):
    pass


def _book_catalog():
    books = Book.objects.annotate(
        average_rating=Avg("reviews__rating")
    ).order_by("-id")[:40]
    return [
        {
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "price": str(book.price),
            "description": book.description[:350],
            "rating": (
                round(book.average_rating, 1)
                if book.average_rating is not None
                else None
            ),
        }
        for book in books
    ]


def _local_recommendation(question, catalog):
    if not catalog:
        return "Hozircha katalogda kitob yo'q. Keyinroq yana urinib ko'ring."

    words = {
        word.casefold()
        for word in question.split()
        if len(word) > 2
    }
    ranked_books = sorted(
        catalog,
        key=lambda book: sum(
            word in " ".join(
                str(book[field])
                for field in ("title", "author", "genre", "description")
            ).casefold()
            for word in words
        ),
        reverse=True,
    )
    recommendations = ranked_books[:3]
    lines = [
        "Hozircha AI API kaliti ulanmagan, ammo Bookify katalogidan "
        "sizga mos kitoblarni topdim:"
    ]
    for book in recommendations:
        lines.append(
            f"- {book['title']} — {book['author']} "
            f"({book['genre']}, {book['price']} so'm)"
        )
    lines.append(
        "Aniqroq tavsiya uchun janr, muallif yoki qaysi mavzudagi kitob "
        "kerakligini yozing."
    )
    return "\n".join(lines)


def answer_question(question):
    catalog = _book_catalog()
    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not groq_api_key and not gemini_api_key and not openrouter_api_key:
        return _local_recommendation(question, catalog)
    use_openrouter = bool(openrouter_api_key)
    use_groq = bool(groq_api_key and not gemini_api_key and not use_openrouter)

    system_prompt = (
        "Sen Bookify onlayn kitob do'konining o'zbek tilida javob beradigan "
        "kitob yordamchisisan. Faqat quyidagi katalogdagi ma'lumotlarga "
        "tayangan holda kitob tavsiya qil, kitoblar haqida savollarga javob "
        "ber va narxlarni ko'rsat. Katalogda yo'q ma'lumotni o'ylab topma. "
        "Savol kitoblarga aloqador bo'lmasa, muloyimlik bilan Bookify "
        "kitoblari haqida so'rashni taklif qil. Qisqa va tushunarli yoz.\n\n"
        f"Katalog: {json.dumps(catalog, ensure_ascii=False)}"
    )
    if use_openrouter:
        provider = "OpenRouter"
        payload = json.dumps(
            {
                "model": os.environ.get(
                    "OPENROUTER_MODEL", "openrouter/free"
                ),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                "temperature": 0.5,
                "max_tokens": 500,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openrouter_api_key}",
                "X-Title": "Bookify",
            },
            method="POST",
        )
    elif use_groq:
        provider = "Groq"
        payload = json.dumps(
            {
                "model": os.environ.get(
                    "GROQ_MODEL", "llama-3.3-70b-versatile"
                ),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                "temperature": 0.5,
                "max_tokens": 500,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {groq_api_key}",
            },
            method="POST",
        )
    else:
        provider = "Gemini"
        prompt = f"{system_prompt}\n\nFoydalanuvchi savoli: {question}"
        payload = json.dumps(
            {"contents": [{"parts": [{"text": prompt}]}]},
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.5-flash:generateContent",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": gemini_api_key,
            },
            method="POST",
        )

    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        if use_openrouter or use_groq:
            answer = result["choices"][0]["message"]["content"].strip()
        else:
            answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        if not answer:
            raise AssistantUnavailable(f"{provider} returned an empty answer")
        return answer
    except HTTPError as error:
        logger.warning("%s API returned HTTP %s", provider, error.code)
        raise AssistantUnavailable from error
    except (URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError) as error:
        logger.warning("%s API request failed: %s", provider, error)
        raise AssistantUnavailable from error
