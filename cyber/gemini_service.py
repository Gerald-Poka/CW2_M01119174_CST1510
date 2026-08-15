import logging

from django.conf import settings

from google import genai

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_content(prompt: str, model: str = MODEL):
    """Return the text of a single Gemini completion. Returns None on error."""
    try:
        client = get_client()
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text.strip()
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        return None


def stream_content(prompt: str, model: str = MODEL):
    """Yield text chunks from a streaming Gemini completion."""
    try:
        client = get_client()
        for chunk in client.models.generate_content_stream(
            model=model, contents=prompt
        ):
            if getattr(chunk, "text", None):
                yield chunk.text
    except Exception as e:
        logger.error("Gemini streaming error: %s", e)
        if "RESOURCE_EXHAUSTED" in str(e):
            yield "AI assistant API quota exceeded. Please wait a while."
        else:
            yield "An unexpected error occurred while contacting AI."
