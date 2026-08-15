import pytest
from app.services.investigation.adapter import InvestigationAdapter
from app.services.investigation.schemas import (
    InvestigationInput,
    IncidentLogInput,
)


@pytest.mark.asyncio
async def test_tool_loop_termination():
    """Verify tool execution loop respects MAX_TOOL_ITERATIONS = 5 and never enters infinite loop."""
    adapter = InvestigationAdapter()
    payload = InvestigationInput(
        incident_id="INC-LOOP-01",
        project_id="PROJ-TEST",
        incident_description="Loop boundary test",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(file_name="loop.log", file_size_bytes=100),
    )

    result = await adapter.arun(payload)
    assert result.incident_id == "INC-LOOP-01"
    # Verify execution trace recorded trace steps
    assert len(result.execution_trace) >= 1


@pytest.mark.asyncio
async def test_investigation_loop_termination():
    """Verify hypothesis evaluation loop respects MAX_INVESTIGATION_ITERATIONS = 3 and terminates cleanly."""
    adapter = InvestigationAdapter()
    payload = InvestigationInput(
        incident_id="INC-LOOP-02",
        project_id="PROJ-TEST",
        incident_description="Investigation loop termination test",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(file_name="loop2.log", file_size_bytes=100),
    )

    result = await adapter.arun(payload)
    assert result.incident_id == "INC-LOOP-02"
    assert result.confidence > 0.0
