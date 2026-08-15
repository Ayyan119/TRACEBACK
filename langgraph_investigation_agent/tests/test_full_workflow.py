import pytest
from app.graph.workflow import build_investigation_graph

@pytest.mark.asyncio
async def test_full_investigation_workflow():
    graph = build_investigation_graph()
    
    input_state = {
        "investigation_id": "inv-test-full",
        "project_id": "art-gallary",
        "incident_id": "INC-1001",
        "incident_description": "Checkout service returning HTTP 504 gateway timeout due to database lock contention.",
        "incident_log_reference": {
            "file_name": "checkout_app.log",
            "file_size_bytes": 1048576
        },
        "services": ["checkout-service"],
        "service_metadata": {},
        "incident_documents": [
            {
                "name": "Database Connection Pool Diagnostic.pdf",
                "content": "Diagnostics report showing connection pool max_connections=100 reached."
            }
        ],
        "incident_images": [
            {
                "title": "Grafana Screenshot 504 Error",
                "file_path": "/path/to/screenshot.png"
            }
        ]
    }

    final_state = await graph.ainvoke(input_state)

    assert final_state["investigation_id"] == "inv-test-full"
    assert len(final_state["accepted_evidence"]) >= 3
    assert len(final_state["hypotheses"]) > 0
    assert final_state["selected_hypothesis"] is not None
    assert final_state["confidence"] > 0.0
    assert final_state["evidence_sufficient"] is True
    assert "final_report" in final_state
    assert final_state["final_report"]["confidence"] > 0.0
    assert len(final_state["execution_trace"]) >= 12
