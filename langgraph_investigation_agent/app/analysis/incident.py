import logging
from typing import List, Dict, Any
from langgraph_investigation_agent.app.models.structured_models import IncidentAnalysisDecision
from langgraph_investigation_agent.app.models.llm import get_structured_llm
from langgraph_investigation_agent.app.prompts.incident_prompts import INCIDENT_ANALYZER_SYSTEM_PROMPT

logger = logging.getLogger("langgraph_agent.analysis.incident")


async def analyze_incident_needs(
    description: str,
    accepted_evidence: List[Dict[str, Any]],
    retrieved_logs: List[Dict[str, Any]],
) -> IncidentAnalysisDecision:
    """Self-RAG decision: determines if knowledge base or previous incident search is required using LLM reasoning."""
    structured_llm = get_structured_llm(IncidentAnalysisDecision)
    if structured_llm is not None:
        try:
            prompt = (
                f"{INCIDENT_ANALYZER_SYSTEM_PROMPT}\n\n"
                f"INCIDENT CONTEXT:\n"
                f"- Description: {description}\n"
                f"- Accepted Evidence Count: {len(accepted_evidence)}\n"
                f"- Retrieved Logs Count: {len(retrieved_logs)}\n\n"
                f"Determine if Qdrant runbook knowledge base or past resolved incident retrieval is required."
            )
            decision = await structured_llm.ainvoke(prompt)
            if decision:
                return decision
        except Exception as e:
            logger.warning(f"LLM incident analyzer failed: {e}")

    # Fallback heuristic decision
    combined_text = (description + " " + str(accepted_evidence) + " " + str(retrieved_logs)).lower()
    needs_retrieval = len(description) > 20 or any(kw in combined_text for kw in ["runbook", "error", "exception", "timeout", "fail", "slow"])
    needs_past_incidents = any(kw in combined_text for kw in ["previous", "history", "outage", "recurring"])
    
    queries = [f"{description[:100]} troubleshooting runbook"] if needs_retrieval else []

    return IncidentAnalysisDecision(
        retrieval_required=needs_retrieval,
        retrieval_reason="Technical knowledge base runbooks recommended based on incident symptom keywords." if needs_retrieval else "Telemetry logs and description provide sufficient self-contained evidence.",
        search_queries=queries,
        relevant_services=["target-service"],
        technical_topics=["troubleshooting"],
        previous_incident_search_required=needs_past_incidents,
    )
