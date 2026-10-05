import time

from google import genai
from google.genai import types

from .config import API_KEY, FALLBACK_MODELS

_client = None
BUSY_CODES = (429, 500, 503, 504)


def _get_client():
    global _client
    if _client is None:
        if not API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is missing. Add it to the .env file and restart the server.")
        _client = genai.Client(api_key=API_KEY)
    return _client


def _is_busy(exc):
    text = str(exc).lower()
    return getattr(exc, "code", None) in BUSY_CODES or "overloaded" in text or "unavailable" in text


def ask(prompt, model, fallback=None, json_mode=False):
    """Ask Gemini. Retries when the model is busy, then moves down the fallback list."""
    config = types.GenerateContentConfig(response_mime_type="application/json") if json_mode else None
    last = None
    for name in dict.fromkeys([model, fallback, *FALLBACK_MODELS]):
        if not name:
            continue
        for attempt in range(2):
            try:
                reply = _get_client().models.generate_content(model=name, contents=prompt, config=config)
                if reply.text:
                    return reply.text.strip()
                break
            except Exception as exc:
                last = exc
                if _is_busy(exc) and attempt == 0:
                    time.sleep(3)
                    continue
                break
    if last is not None and _is_busy(last):
        raise RuntimeError("Gemini is very busy right now. Wait a minute and try again.")
    detail = f"{type(last).__name__}: {str(last)[:200]}" if last else "empty reply"
    raise RuntimeError(f"Gemini could not answer right now ({detail}).")