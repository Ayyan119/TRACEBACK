import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMSummarizerService:
    """Generates concise technical summaries for Incident Documents using Groq Llama-3.3 or Gemini API."""

    def summarize_incident_text(self, text: str, filename: str, max_chars: int = 1500) -> str:
        """Summarizes extracted incident document text using Groq LLM API with fallback to deterministic extractive summary."""
        if not text or not text.strip():
            return f"Incident document '{filename}' contains no extractable text."

        groq_api_key = getattr(settings, "GROQ_API_KEY", "") or ""

        if groq_api_key:
            try:
                from groq import Groq

                client = Groq(api_key=groq_api_key)
                prompt = (
                    f"You are an SRE incident responder. Summarize the following incident document '{filename}' "
                    f"in 3 to 5 concise bullet points highlighting key errors, root cause hints, affected systems, and timestamps.\n\n"
                    f"DOCUMENT CONTENT:\n{text[:6000]}"
                )
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a concise SRE Incident Analysis assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=400,
                    temperature=0.2,
                )
                summary_text = response.choices[0].message.content.strip()
                if summary_text:
                    logger.info(f"Successfully generated Groq LLM summary for '{filename}'")
                    return f"### AI Incident Document Summary ({filename})\n\n{summary_text}"
            except Exception as e:
                logger.warning(f"Groq API summarization warning for '{filename}': {e}")

        # Deterministic Extractive Summary Fallback
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        first_excerpt = "\n\n".join(paragraphs[:3])[:max_chars]
        return (
            f"### Incident Document Summary ({filename})\n\n"
            f"**Extracted Content Excerpt:**\n{first_excerpt}..."
        )


llm_summarizer = LLMSummarizerService()
