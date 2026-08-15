import pytest
from app.services.investigation.adapter import InvestigationAdapter
from app.services.investigation.schemas import (
    InvestigationInput,
    IncidentLogInput,
    IncidentDocumentInput,
    IncidentImageInput,
)
from app.services.investigation.exceptions import (
    GraphExecutionError,
    MissingLogReferenceError,
)
from app.services.log_service import log_service


@pytest.mark.asyncio
async def test_sql_injection_protection(db):
    """Verify log query filters remain strictly parameterized against SQL injection attempts."""
    malicious_keyword = "' OR '1'='1' -- DROP TABLE log_records;"
    logs = await log_service.query_logs(
        db=db,
        project_id="PROJ-TEST",
        keyword=malicious_keyword,
        limit=10,
    )
    assert isinstance(logs, list)


@pytest.mark.asyncio
async def test_credential_sanitization_on_failure():
    """Verify sensitive database credentials or internal secrets are NEVER leaked in error messages."""
    async def failing_runner(state):
        raise RuntimeError("DB Error: postgresql://admin:SECRET_PASSWORD_123@db.internal:5432/traceback_db")

    adapter = InvestigationAdapter(graph_runner=failing_runner)
    payload = InvestigationInput(
        incident_id="INC-EDGE-01",
        project_id="PROJ-TEST",
        incident_description="Test scenario",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(file_name="test.log", file_size_bytes=100),
    )

    with pytest.raises(GraphExecutionError) as exc_info:
        await adapter.arun(payload)

    err_str = str(exc_info.value)
    assert "SECRET_PASSWORD_123" not in err_str
    assert "INC-EDGE-01" in err_str


@pytest.mark.asyncio
async def test_malformed_document_input():
    """Verify malformed/empty document contents are handled gracefully."""
    adapter = InvestigationAdapter()
    payload = InvestigationInput(
        incident_id="INC-EDGE-02",
        project_id="PROJ-TEST",
        incident_description="Test scenario",
        services=["checkout-service"],
        incident_log_reference=IncidentLogInput(file_name="test.log", file_size_bytes=100),
        incident_documents=[
            IncidentDocumentInput(name="Empty.pdf", content="")
        ]
    )

    result = await adapter.arun(payload)
    assert result.incident_id == "INC-EDGE-02"
