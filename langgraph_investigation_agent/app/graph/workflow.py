import logging
from langgraph.graph import StateGraph, START, END

from app.graph.state import InvestigationState
from app.graph.nodes import (
    initialize_state_node,
    process_images_node,
    process_documents_node,
    collect_evidence_node,
    reason_with_tools_node,
    execute_log_tools_node,
    incident_analyzer_node,
    retrieve_knowledge_node,
    retrieve_previous_incidents_node,
    rerank_retrieved_information_node,
    analyze_evidence_node,
    generate_hypotheses_node,
    evaluate_hypotheses_node,
    generate_final_report_node,
)
from app.graph.routers import (
    route_after_reason_with_tools,
    route_after_incident_analysis,
    route_after_hypothesis_evaluation,
)

logger = logging.getLogger("langgraph_agent.graph.workflow")


def build_investigation_graph():
    """Constructs and compiles the complete TRACEBACK LangGraph AI Investigation Agent workflow graph."""
    builder = StateGraph(InvestigationState)

    # 1. Register All 14 Graph Nodes
    builder.add_node("initialize_state", initialize_state_node)
    builder.add_node("process_images", process_images_node)
    builder.add_node("process_documents", process_documents_node)
    builder.add_node("collect_evidence", collect_evidence_node)
    builder.add_node("reason_with_tools", reason_with_tools_node)
    builder.add_node("execute_log_tools", execute_log_tools_node)
    builder.add_node("incident_analyzer", incident_analyzer_node)
    builder.add_node("retrieve_knowledge", retrieve_knowledge_node)
    builder.add_node("retrieve_previous_incidents", retrieve_previous_incidents_node)
    builder.add_node("rerank_retrieved_information", rerank_retrieved_information_node)
    builder.add_node("analyze_evidence", analyze_evidence_node)
    builder.add_node("generate_hypotheses", generate_hypotheses_node)
    builder.add_node("evaluate_hypotheses", evaluate_hypotheses_node)
    builder.add_node("generate_final_report", generate_final_report_node)

    # 2. Parallel Processing Branch & Evidence Collection
    builder.add_edge(START, "initialize_state")
    builder.add_edge("initialize_state", "process_images")
    builder.add_edge("initialize_state", "process_documents")
    builder.add_edge("process_images", "collect_evidence")
    builder.add_edge("process_documents", "collect_evidence")

    # 3. Main Loop Re-entry Edge
    builder.add_edge("collect_evidence", "reason_with_tools")

    # 4. Tool Reasoning Loop Conditional Router
    builder.add_conditional_edges(
        "reason_with_tools",
        route_after_reason_with_tools,
        {
            "execute_log_tools": "execute_log_tools",
            "incident_analyzer": "incident_analyzer",
        },
    )
    builder.add_edge("execute_log_tools", "reason_with_tools")

    # 5. Self-RAG Retrieval Conditional Router
    builder.add_conditional_edges(
        "incident_analyzer",
        route_after_incident_analysis,
        {
            "retrieve_knowledge": "retrieve_knowledge",
            "analyze_evidence": "analyze_evidence",
        },
    )

    # Retrieval Sub-Pipeline
    builder.add_edge("retrieve_knowledge", "retrieve_previous_incidents")
    builder.add_edge("retrieve_previous_incidents", "rerank_retrieved_information")
    builder.add_edge("rerank_retrieved_information", "analyze_evidence")

    # Synthesis, Hypothesis Generation & Evaluation
    builder.add_edge("analyze_evidence", "generate_hypotheses")
    builder.add_edge("generate_hypotheses", "evaluate_hypotheses")

    # 6. Investigation Loop Conditional Router (Sufficiency & Iteration Control)
    builder.add_conditional_edges(
        "evaluate_hypotheses",
        route_after_hypothesis_evaluation,
        {
            "reason_with_tools": "reason_with_tools",
            "generate_final_report": "generate_final_report",
        },
    )

    # Final RCA Report & Termination
    builder.add_edge("generate_final_report", END)

    # Compile Graph
    graph = builder.compile()
    logger.info("TRACEBACK Complete Investigation Graph compiled successfully!")
    return graph
