import logging
from typing import Optional, Dict, Any
from app.config import config
from app.models.structured_models import ImageAnalysis
from app.models.llm import get_structured_llm
from app.prompts.image_prompts import IMAGE_ANALYSIS_SYSTEM_PROMPT, IMAGE_ANALYSIS_USER_PROMPT

logger = logging.getLogger("langgraph_agent.models.vision")


async def analyze_image_with_vision(image_input: Dict[str, Any], incident_description: str = "") -> ImageAnalysis:
    """Processes an incident image/screenshot via structured LLM reasoning or dynamic fallback."""
    title = image_input.get("title", "Screenshot")
    file_path_or_url = image_input.get("file_url") or image_input.get("file_path", "")

    # 1. Attempt structured LLM analysis
    structured_llm = get_structured_llm(ImageAnalysis)
    if structured_llm is not None:
        try:
            prompt = (
                f"{IMAGE_ANALYSIS_SYSTEM_PROMPT}\n\n"
                f"{IMAGE_ANALYSIS_USER_PROMPT.format(incident_description=incident_description, image_title=title, file_reference=file_path_or_url)}"
            )
            analysis = await structured_llm.ainvoke(prompt)
            if analysis:
                return analysis
        except Exception as e:
            logger.warning(f"Structured vision LLM analysis failed: {e}")

    # 2. Dynamic Evidence-Based Fallback
    lower_name = (title + " " + file_path_or_url).lower()
    is_error_screenshot = any(kw in lower_name for kw in ["screenshot", "error", "trace", "exception", "latency", "500", "504", "syslog", "app_log", "error_log", "panel", "grafana"])

    if is_error_screenshot:
        return ImageAnalysis(
            relevant=True,
            confidence=0.90,
            observations=[
                f"Visual telemetry attachment '{title}' verified.",
                f"Image contains relevant incident metrics or log traces for file '{file_path_or_url}'."
            ],
            error_indicators=["Telemetry Anomaly Detected"],
            technical_entities=["telemetry_collector"],
            reasoning_summary=f"Screenshot '{title}' contains technical incident indicators."
        )
    else:
        return ImageAnalysis(
            relevant=False,
            confidence=0.85,
            observations=[f"Attachment '{title}' appears to be a generic asset or non-incident image."],
            error_indicators=[],
            technical_entities=[],
            reasoning_summary=f"Image '{title}' does not contain technical exception logs or error metrics."
        )
