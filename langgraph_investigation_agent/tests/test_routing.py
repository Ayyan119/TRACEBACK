import pytest
from app.graph.routers import (
    route_after_reason_with_tools,
    route_after_incident_analysis,
    route_after_hypothesis_evaluation,
)

def test_route_after_reason_with_tools():
    state1 = {"tool_decision": "query_logs", "tool_iterations": 1}
    assert route_after_reason_with_tools(state1) == "execute_log_tools"

    state2 = {"tool_decision": "no_tool", "tool_iterations": 1}
    assert route_after_reason_with_tools(state2) == "incident_analyzer"

    state3 = {"tool_decision": "query_logs", "tool_iterations": 5}
    assert route_after_reason_with_tools(state3) == "incident_analyzer"

def test_route_after_incident_analysis():
    state1 = {"retrieval_required": True}
    assert route_after_incident_analysis(state1) == "retrieve_knowledge"

    state2 = {"retrieval_required": False}
    assert route_after_incident_analysis(state2) == "analyze_evidence"

def test_route_after_hypothesis_evaluation():
    # Evidence sufficient -> route to final report
    state1 = {"evidence_sufficient": True, "investigation_iterations": 1}
    assert route_after_hypothesis_evaluation(state1) == "generate_final_report"

    # Evidence insufficient but under max iterations -> route to investigation loop (reason_with_tools)
    state2 = {"evidence_sufficient": False, "investigation_iterations": 1}
    assert route_after_hypothesis_evaluation(state2) == "reason_with_tools"

    # Evidence insufficient but max iterations reached (3) -> route to generate_final_report
    state3 = {"evidence_sufficient": False, "investigation_iterations": 3}
    assert route_after_hypothesis_evaluation(state3) == "generate_final_report"
