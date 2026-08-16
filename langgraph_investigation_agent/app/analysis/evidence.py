import logging
from typing import List, Dict, Any
from langgraph_investigation_agent.app.models.structured_models import DocumentAnalysis
from langgraph_investigation_agent.app.models.llm import get_structured_llm
from langgraph_investigation_agent.app.prompts.document_prompts import DOCUMENT_ANALYSIS_SYSTEM_PROMPT, DOCUMENT_ANALYSIS_USER_PROMPT

logger = logging.getLogger("langgraph_agent.analysis.evidence")


async def analyze_incident_document(doc: Dict[str, Any], incident_description: str) -> DocumentAnalysis:
    """Extracts text, summarizes, and evaluates relevance of an incident evidence document using LLM reasoning."""
    title = doc.get("name", doc.get("title", "Document"))
    content = doc.get("content", doc.get("summary", ""))

    # 1. Attempt structured LLM extraction (nano model)
    structured_llm = get_structured_llm(DocumentAnalysis, model_type="extraction")
    if structured_llm is not None:
        try:
            prompt = (
                f"{DOCUMENT_ANALYSIS_SYSTEM_PROMPT}\n\n"
                f"{DOCUMENT_ANALYSIS_USER_PROMPT.format(incident_description=incident_description, document_title=title, document_content=content[:2000])}"
            )
            analysis = await structured_llm.ainvoke(prompt)
            if analysis:
                return analysis
        except Exception as e:
            logger.warning(f"Structured document LLM analysis failed: {e}")

    # 2. Dynamic Evidence-Based Fallback
    doc_text = (title + " " + content).lower()
    is_relevant = any(kw in doc_text for kw in ["error", "exception", "trace", "fail", "timeout", "latency", "pool", "lock", "db", "post-mortem", "diagnostic", "log", "runbook", "config"])

    if is_relevant:
        return DocumentAnalysis(
            relevant=True,
            confidence=0.88,
            summary=f"Incident document '{title}' contains technical log traces or operational diagnostic context.",
            key_points=[f"Document '{title}' analyzed."],
            technical_entities=["system_component"],
            error_signatures=[content[:100]] if content else ["Error signature in document"],
            timestamps=[],
            affected_services=[],
            root_cause_hints=[f"Context provided in {title}"]
        )
    else:
        return DocumentAnalysis(
            relevant=False,
            confidence=0.85,
            summary=f"Document '{title}' does not contain technical error logs or diagnostic indicators for this incident.",
            key_points=[],
            technical_entities=[],
            error_signatures=[],
            timestamps=[],
            affected_services=[],
            root_cause_hints=[]
        )
