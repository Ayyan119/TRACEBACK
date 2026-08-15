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
        
        # Summary string fallback
        summary = final_state.get("investigation_summary")
        if not summary:
            primary_h = final_state.get("selected_hypothesis", {})
            summary = f"Investigation completed for {incident_id}. Primary root cause: {primary_h.get('title', 'Unknown')}."

        # Extract structured outputs
        final_report = final_state.get("final_report")
        selected_hypothesis = final_state.get("selected_hypothesis")
        hypotheses = final_state.get("hypotheses", [])
        evidence_analysis = final_state.get("evidence_analysis")
        accepted_evidence = final_state.get("accepted_evidence", [])
        rejected_evidence = final_state.get("rejected_evidence", [])
        log_query_history = final_state.get("log_query_history", [])
        execution_trace = final_state.get("execution_trace", [])

        # Check for errors in state
        errors = final_state.get("errors", [])
        status = "COMPLETED"
        if errors and not selected_hypothesis and not final_report:
            status = "FAILED"

        result = InvestigationResult(
            investigation_id=investigation_id,
            incident_id=incident_id,
            status=status,
            confidence=round(confidence, 2),
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
            f"(Confidence: {result.confidence}%, Accepted Evidence: {len(result.accepted_evidence)})"
        )
        return result
