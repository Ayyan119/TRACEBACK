import logging
from app.config import config
from app.graph.state import InvestigationState

logger = logging.getLogger("langgraph_agent.graph.routers")


def route_after_reason_with_tools(state: InvestigationState) -> str:
    """Routing function after reason_with_tools node."""
    decision = state.get("tool_decision", "no_tool")
    iterations = state.get("tool_iterations", 0)
    
    if decision == "query_logs" and iterations < config.MAX_TOOL_ITERATIONS:
        logger.info(f"Router: decision is 'query_logs' (iteration {iterations}) -> routing to execute_log_tools")
        return "execute_log_tools"
    else:
        logger.info(f"Router: decision is '{decision}' or max iterations reached ({iterations}) -> routing to incident_analyzer")
        return "incident_analyzer"


def route_after_incident_analysis(state: InvestigationState) -> str:
    """Routing function after incident_analyzer node (Self-RAG style decision)."""
    retrieval_required = state.get("retrieval_required", False)
    
    if retrieval_required:
        logger.info("Router: retrieval_required is True -> routing to retrieve_knowledge")
        return "retrieve_knowledge"
    else:
        logger.info("Router: retrieval_required is False -> routing to analyze_evidence")
        return "analyze_evidence"


def route_after_hypothesis_evaluation(state: InvestigationState) -> str:
    """Routing function after evaluate_hypotheses node (Investigation Loop decision)."""
    is_sufficient = state.get("evidence_sufficient", True)
    inv_iterations = state.get("investigation_iterations", 0)
    
    if not is_sufficient and inv_iterations < config.MAX_INVESTIGATION_ITERATIONS:
        logger.info(f"Router: evidence is insufficient (cycle {inv_iterations}/{config.MAX_INVESTIGATION_ITERATIONS}) -> looping back to reason_with_tools")
        return "reason_with_tools"
    else:
        logger.info(f"Router: evidence is sufficient or max investigation iterations reached ({inv_iterations}/{config.MAX_INVESTIGATION_ITERATIONS}) -> routing to generate_final_report")
        return "generate_final_report"
