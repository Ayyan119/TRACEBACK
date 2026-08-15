import logging
from typing import Type, Any, Optional
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.config import config

logger = logging.getLogger("langgraph_agent.models.llm")


def get_reasoning_llm() -> Optional[BaseChatModel]:
    """Returns the primary tool & reasoning language model."""
    # 1. Try Google Gemini (Primary LLM)
    if config.GOOGLE_API_KEY:
        try:
            return ChatGoogleGenerativeAI(
                model=config.DEFAULT_LLM_MODEL or "gemini-3.5-flash",
                google_api_key=config.GOOGLE_API_KEY,
                temperature=0.1,
                max_retries=0,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize ChatGoogleGenerativeAI: {e}")

    # 2. Try Groq (Fallback)
    if config.GROQ_API_KEY:
        try:
            return ChatGroq(
                model=config.FALLBACK_LLM_MODEL or "llama-3.3-70b-versatile",
                groq_api_key=config.GROQ_API_KEY,
                temperature=0.1,
                max_retries=0,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize ChatGroq: {e}")

    logger.warning("No active LLM API key detected.")
    return None


def get_structured_llm(output_schema: Type[BaseModel]) -> Any:
    """Returns a model configured with structured output (with schema enforcement)."""
    llm = get_reasoning_llm()
    if llm is not None:
        try:
            return llm.with_structured_output(output_schema)
        except Exception as e:
            logger.warning(f"with_structured_output failed: {e}")
    return None
