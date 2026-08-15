import pytest
from app.graph.workflow import build_investigation_graph

@pytest.mark.asyncio
async def test_scenario_no_optional_evidence():
    """Scenario A: Description + mandatory log only (no documents, no images)."""
    graph = build_investigation_graph()
    input_state = {
        "investigation_id": "inv-scenario-a-test",
        "project_id": "art-gallary",
        "incident_id": "INC-1001",
        "incident_description": "Checkout service returning HTTP 504 gateway timeouts.",
        "incident_log_reference": {"file_name": "app.log"},
        "services": ["checkout-service"],
        "incident_documents": [],
        "incident_images": []
    }
    final_state = await graph.ainvoke(input_state)
    assert len(final_state["accepted_evidence"]) >= 2
    assert len(final_state["hypotheses"]) > 0

@pytest.mark.asyncio
async def test_max_tool_iterations_exit():
    """Verifies that max 5 tool iterations prevents infinite loops."""
    graph = build_investigation_graph()
    input_state = {
        "investigation_id": "inv-max-iter",
        "project_id": "art-gallary",
        "incident_id": "INC-1001",
        "incident_description": "Checkout service outage",
        "services": ["checkout-service"],
        "tool_iterations": 5,  # Force initial tool_iterations to 5
        "tool_decision": "query_logs",
    }
    final_state = await graph.ainvoke(input_state)
    # Graph must exit tool loop and complete hypotheses node
    assert len(final_state["hypotheses"]) > 0
