import asyncio
import random
import logging
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger("langgraph_agent.models.llm_invoker")

T = TypeVar("T")

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.5
BACKOFF_FACTOR = 2.0
JITTER_RANGE = (0.1, 0.5)


async def invoke_llm_with_orchestration(
    invoker_fn: Callable[..., Any],
    *args: Any,
    provider_name: str = "openai",
    node_name: str = "unknown_node",
    **kwargs: Any,
) -> Optional[Any]:
    """
    Centralized LLM request orchestrator.
    Handles controlled retries with exponential backoff and jitter for transient 429/503 errors.
    Prevents uncontrolled request storms while maintaining detailed audit logs.
    """
    attempt = 0
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            # Execute async LLM invocation
            if asyncio.iscoroutinefunction(invoker_fn):
                result = await invoker_fn(*args, **kwargs)
            else:
                result = invoker_fn(*args, **kwargs)
            return result
        except Exception as e:
            err_str = str(e)
            is_transient = (
                "503" in err_str
                or "429" in err_str
                or "RESOURCE_EXHAUSTED" in err_str
                or "UNAVAILABLE" in err_str
                or "Service Unavailable" in err_str
                or "high demand" in err_str
            )
            
            if not is_transient or attempt >= MAX_RETRIES:
                logger.warning(
                    f"LLM invocation failed permanently [node={node_name}, provider={provider_name}, "
                    f"attempt={attempt}/{MAX_RETRIES}]: {e}"
                )
                raise e

            # Calculate backoff delay with jitter
            backoff = (INITIAL_BACKOFF_SECONDS * (BACKOFF_FACTOR ** (attempt - 1))) + random.uniform(*JITTER_RANGE)
            logger.warning(
                f"LLM call failed with transient error [node={node_name}, provider={provider_name}, "
                f"status={'503/429' if is_transient else 'error'}, attempt={attempt}/{MAX_RETRIES}, "
                f"backoff={backoff:.2f}s]: {err_str[:120]}"
            )
            await asyncio.sleep(backoff)
            
    return None
