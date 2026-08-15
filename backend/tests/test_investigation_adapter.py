import os
import sys
import pytest
import asyncio

# Setup sys.path
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
agent_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "langgraph_investigation_agent"))

if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.services.investigation.schemas import (
    InvestigationInput,
    IncidentLogInput,
    IncidentDocumentInput,
    IncidentImageInput,
    InvestigationResult,
)
from app.services.investigation.input_adapter import InputAdapter
from app.services.investigation.output_adapter import OutputAdapter
from app.services.investigation.adapter import InvestigationAdapter
from app.services.investigation.exceptions import (
    MissingLogReferenceError,
    InvalidInputError,
    GraphExecutionError,
)


def _get_real_graph():
    """Helper to dynamically load real LangGraph workflow avoiding top-level 'app' package collision."""
    saved_modules = {k: v for k, v in sys.modules.items() if k == "app" or k.startswith("app.")}

    try:
        if agent_root not in sys.path:
            sys.path.insert(0, agent_root)

        for k in list(sys.modules.keys()):
            if k == "app" or k.startswith("app."):
                del sys.modules[k]

        import app.graph.workflow as agent_workflow
        graph = agent_workflow.build_investigation_graph()
        return graph
    finally:
        for k in list(sys.modules.keys()):
            if k == "app" or k.startswith("app."):
                del sys.modules[k]
        sys.modules.update(saved_modules)


# --- TEST 1: Log Only Input ---
def test_input_adapter_log_only():
    payload = InvestigationInput(
        incident_id="INC-3001",
        project_id="PROJ-100",
        incident_description="Database connection pool timeout",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(
            file_name="app_telemetry.log",
            file_size_bytes=1048576,
            log_type="telemetry"
        ),
        incident_documents=[],
        incident_images=[],
    )
    
    state = InputAdapter.to_investigation_state(payload)
    
    assert state["incident_id"] == "INC-3001"
    assert state["project_id"] == "PROJ-100"
    assert state["incident_description"] == "Database connection pool timeout"
    assert state["incident_log_reference"]["file_name"] == "app_telemetry.log"
    assert len(state["incident_documents"]) == 0
    assert len(state["incident_images"]) == 0


# --- TEST 2: Log + Documents ---
def test_input_adapter_log_and_documents():
    payload = InvestigationInput(
        incident_id="INC-3002",
        project_id="PROJ-100",
        incident_description="PostgreSQL active connections 100/100 limit reached",
        services=["checkout-service", "postgresql_db"],
        incident_log_reference=IncidentLogInput(
            file_name="postgres_err.log",
            file_size_bytes=524288,
        ),
        incident_documents=[
            IncidentDocumentInput(name="Diagnostics.pdf", content="Pool limit reached.")
        ],
        incident_images=[],
    )
    
    state = InputAdapter.to_investigation_state(payload)
    
    assert len(state["incident_documents"]) == 1
    assert state["incident_documents"][0]["name"] == "Diagnostics.pdf"
    assert len(state["incident_images"]) == 0


# --- TEST 3: Log + Images ---
def test_input_adapter_log_and_images():
    payload = InvestigationInput(
        incident_id="INC-3003",
        project_id="PROJ-100",
        incident_description="Grafana dashboard showing 504 latency spike",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(
            file_name="grafana.log",
            file_size_bytes=204800,
        ),
        incident_documents=[],
        incident_images=[
            IncidentImageInput(title="Grafana 504 Spike", file_url="https://storage.local/img1.png")
        ],
    )
    
    state = InputAdapter.to_investigation_state(payload)
    
    assert len(state["incident_documents"]) == 0
    assert len(state["incident_images"]) == 1
    assert state["incident_images"][0]["title"] == "Grafana 504 Spike"


# --- TEST 4: Log + Documents + Images ---
def test_input_adapter_log_documents_and_images():
    payload = InvestigationInput(
        incident_id="INC-3004",
        project_id="PROJ-100",
        incident_description="Complete outage scenario with telemetry and documents",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(
            file_name="full_telemetry.log",
            file_size_bytes=2097152,
        ),
        incident_documents=[
            IncidentDocumentInput(name="Runbook.pdf", content="Troubleshooting guide.")
        ],
        incident_images=[
            IncidentImageInput(title="Screenshot", file_url="https://storage.local/img2.png")
        ],
    )
    
    state = InputAdapter.to_investigation_state(payload)
    
    assert len(state["incident_documents"]) == 1
    assert len(state["incident_images"]) == 1


# --- TEST 5: Missing Log Validation Error ---
def test_input_adapter_missing_log_raises_error():
    with pytest.raises(Exception):
        # Pydantic validation fails if incident_log_reference is None
        InvestigationInput(
            incident_id="INC-3005",
            project_id="PROJ-100",
            incident_description="Missing log test",
            services=["checkout-service"],
            incident_log_reference=None,  # Invalid
        )


# --- TEST 6: Mock LangGraph Execution ---
@pytest.mark.asyncio
async def test_adapter_mock_graph_execution():
    async def mock_graph_runner(state):
        return {
            "investigation_id": "inv-mock-999",
            "incident_id": state["incident_id"],
            "confidence": 95.0,
            "investigation_summary": "Mock investigation complete",
            "selected_hypothesis": {"hypothesis_id": "HYP-1", "title": "Mock Root Cause"},
            "hypotheses": [{"hypothesis_id": "HYP-1", "title": "Mock Root Cause"}],
            "accepted_evidence": [{"evidence_id": "EVD-1", "source_name": "log"}],
            "rejected_evidence": [],
            "execution_trace": [{"node": "mock_node", "duration_ms": 1.0}],
        }

    adapter = InvestigationAdapter(graph_runner=mock_graph_runner)
    payload = InvestigationInput(
        incident_id="INC-3006",
        project_id="PROJ-100",
        incident_description="Mock test scenario",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(file_name="test.log", file_size_bytes=100),
    )

    result = await adapter.arun(payload)

    assert isinstance(result, InvestigationResult)
    assert result.incident_id == "INC-3006"
    assert result.investigation_id == "inv-mock-999"
    assert result.confidence == 95.0
    assert result.selected_hypothesis["hypothesis_id"] == "HYP-1"


# --- TEST 7: Graph Failure Error Handling ---
@pytest.mark.asyncio
async def test_adapter_graph_failure_handling():
    async def failing_graph_runner(state):
        raise RuntimeError("Internal secret connection string failure: postgresql://secret:password@host/db")

    adapter = InvestigationAdapter(graph_runner=failing_graph_runner)
    payload = InvestigationInput(
        incident_id="INC-3007",
        project_id="PROJ-100",
        incident_description="Failing scenario",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(file_name="test.log", file_size_bytes=100),
    )

    with pytest.raises(GraphExecutionError) as exc_info:
        await adapter.arun(payload)

    # Verify sensitive error string is NOT leaked in exception message
    assert "secret:password" not in str(exc_info.value)
    assert "INC-3007" in str(exc_info.value)


# --- TEST 8: Empty Optional Fields ---
def test_input_adapter_empty_optional_fields():
    payload = InvestigationInput(
        incident_id="INC-3008",
        project_id="PROJ-100",
        incident_description="Empty optional fields test",
        services=[],
        service_metadata={},
        incident_log_reference=IncidentLogInput(file_name="test.log", file_size_bytes=100),
        incident_documents=[],
        incident_images=[],
    )

    state = InputAdapter.to_investigation_state(payload)

    assert state["services"] == ["default-service"]
    assert state["incident_documents"] == []
    assert state["incident_images"] == []


# --- TEST 9: Real Compiled Graph Smoke Test ---
@pytest.mark.asyncio
async def test_adapter_real_graph_execution_smoke_test():
    real_graph = _get_real_graph()

    async def real_graph_runner(state):
        return await real_graph.ainvoke(state)

    adapter = InvestigationAdapter(graph_runner=real_graph_runner)

    payload = InvestigationInput(
        incident_id="INC-3009",
        project_id="art-gallary",
        incident_description="Checkout service failing with 504 Gateway Timeout due to database connection pool lock contention.",
        services=["checkout-service"],
        service_metadata={"checkout-service": {"environment": "production"}},
        incident_log_reference=IncidentLogInput(
            file_name="checkout_app.log",
            file_size_bytes=1048576,
            log_type="telemetry"
        ),
        incident_documents=[
            IncidentDocumentInput(
                name="Database Connection Pool Diagnostic.pdf",
                content="Diagnostics report showing connection pool max_connections=100 limit reached."
            )
        ],
        incident_images=[
            IncidentImageInput(
                title="Grafana Screenshot 504 Error",
                file_url="https://storage.local/grafana.png"
            )
        ]
    )

    result = await adapter.arun(payload)

    assert isinstance(result, InvestigationResult)
    assert result.incident_id == "INC-3009"
    assert result.confidence > 0.0
    assert result.selected_hypothesis is not None
    assert result.final_report is not None
    assert len(result.accepted_evidence) >= 3
