import logging
from typing import Dict, Any
from app.services.investigation.schemas import InvestigationResult
from app.services.investigation.exceptions import GraphExecutionError

logger = logging.getLogger("traceback.services.investigation.output_adapter")


class OutputAdapter:
    """Translates LangGraph InvestigationState final state into a clean TRACEBACK API InvestigationResult."""

    @staticmethod
    def to_investigation_result(final_state: Dict[str, Any]) -> InvestigationResult:
        """Converts final LangGraph InvestigationState dictionary into InvestigationResult schema."""
        if not final_state or not isinstance(final_state, dict):
            raise GraphExecutionError("Final graph execution state is null or invalid.")

        incident_id = final_state.get("incident_id", "unknown-incident")
        investigation_id = final_state.get("investigation_id", "unknown-investigation")
        confidence = float(final_state.get("confidence", 0.0))
        
        selected_hypothesis = final_state.get("selected_hypothesis", {}) or {}
        root_cause_str = selected_hypothesis.get("likely_root_cause") or selected_hypothesis.get("title") or "Root cause cannot be conclusively determined from the supplied evidence."
        
        summary = final_state.get("investigation_summary")
        if not summary or "FINAL RCA COMPLETE" in summary:
            summary = f"Investigation completed for incident {incident_id}. Primary root cause: {root_cause_str}"

        # Extract structured outputs
        final_report = final_state.get("final_report")
        selected_hypothesis = final_state.get("selected_hypothesis")
        hypotheses = final_state.get("hypotheses", [])
        evidence_analysis = final_state.get("evidence_analysis")
        accepted_evidence = final_state.get("accepted_evidence", [])
        rejected_evidence = final_state.get("rejected_evidence", [])
        log_query_history = final_state.get("log_query_history", [])
        execution_trace = final_state.get("execution_trace", [])

        confidence_source = final_state.get("confidence_source", "llm")
        analysis_status = final_state.get("analysis_status", "success")
        failed_llm_nodes = final_state.get("failed_llm_nodes", [])

        # Check for errors in state
        errors = final_state.get("errors", [])
        status = "COMPLETED"
        if analysis_status == "degraded" or confidence_source == "fallback":
            status = "DEGRADED"
        if errors and not selected_hypothesis and not final_report:
            status = "FAILED"

        result = InvestigationResult(
            investigation_id=investigation_id,
            incident_id=incident_id,
            status=status,
            confidence=round(confidence, 2),
            confidence_source=confidence_source,
            analysis_status=analysis_status,
            failed_llm_nodes=failed_llm_nodes,
            investigation_summary=summary,
            final_report=final_report,
            selected_hypothesis=selected_hypothesis,
            hypotheses=hypotheses,
            evidence_analysis=evidence_analysis,
            accepted_evidence=accepted_evidence,
            rejected_evidence=rejected_evidence,
            log_query_history=log_query_history,
            execution_trace=execution_trace,
        )

        logger.info(
            f"OutputAdapter: Successfully created InvestigationResult for '{incident_id}' "
            f"(Status: {result.status}, Confidence: {result.confidence}%, Source: {confidence_source}, Accepted Evidence: {len(result.accepted_evidence)})"
        )
        return result
