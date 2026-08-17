import logging
from typing import Type, Any, Optional
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph_investigation_agent.app.config import config

logger = logging.getLogger("langgraph_agent.models.llm")


def get_extraction_llm() -> Optional[BaseChatModel]:
    """
    Returns the light fast extraction model for documents/images/summarization.
    Default: gpt-5.4-nano (or gpt-4o-mini).
    """
    if config.OPENAI_API_KEY:
        try:
            return ChatOpenAI(
                model=config.EXTRACTION_LLM_MODEL or "gpt-4o-mini",
                api_key=config.OPENAI_API_KEY,
                temperature=0.0,
                max_retries=0,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize extraction ChatOpenAI: {e}")
    logger.warning("No active OPENAI_API_KEY detected.")
    return None


def get_reasoning_llm() -> Optional[BaseChatModel]:
    """
    Returns the primary reasoning model for hypothesis generation, analysis & RCA.
    Default: gpt-5.4-mini (or gpt-4o-mini).
    """
    if config.OPENAI_API_KEY:
        try:
            return ChatOpenAI(
                model=config.REASONING_LLM_MODEL or "gpt-4o-mini",
                api_key=config.OPENAI_API_KEY,
                temperature=0.1,
                max_retries=0,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize reasoning ChatOpenAI: {e}")

    logger.warning("No active OPENAI_API_KEY detected.")
    return None


def get_structured_llm(output_schema: Type[BaseModel], model_type: str = "reasoning") -> Any:
    """Returns a model configured with structured output (with schema enforcement)."""
    llm = get_extraction_llm() if model_type == "extraction" else get_reasoning_llm()
    if llm is not None:
        try:
            return llm.with_structured_output(output_schema)
        except Exception as e:
            logger.warning(f"with_structured_output failed for model_type={model_type}: {e}")
    return None


async def safe_invoke_structured_llm(
    output_schema: Type[BaseModel],
    prompt: str,
    node_name: str = "unknown_node",
    model_type: str = "reasoning",
) -> Optional[Any]:
    """Invokes structured LLM with exponential backoff, jitter, and error tracking."""
    from langgraph_investigation_agent.app.models.llm_invoker import invoke_llm_with_orchestration

    structured_llm = get_structured_llm(output_schema, model_type=model_type)
    if structured_llm is None:
        return None

    try:
        return await invoke_llm_with_orchestration(
            structured_llm.ainvoke,
            prompt,
            provider_name="openai",
            node_name=node_name,
        )
    except Exception as e:
        logger.warning(f"safe_invoke_structured_llm failed for {node_name}: {e}")
        return None


async def safe_invoke_reasoning_llm(
    prompt: str,
    node_name: str = "unknown_node",
    model_type: str = "reasoning",
) -> Optional[Any]:
    """Invokes reasoning LLM with exponential backoff, jitter, and error tracking."""
    from langgraph_investigation_agent.app.models.llm_invoker import invoke_llm_with_orchestration

    llm = get_extraction_llm() if model_type == "extraction" else get_reasoning_llm()
    if llm is None:
        return None

    try:
        return await invoke_llm_with_orchestration(
            llm.ainvoke,
            prompt,
            provider_name="openai",
            node_name=node_name,
        )
    except Exception as e:
        logger.warning(f"safe_invoke_reasoning_llm failed for {node_name}: {e}")
        return None
