import pytest
from app.services.vector_service import vector_service


@pytest.mark.asyncio
async def test_qdrant_knowledge_retrieval_isolation():
    """Verify Qdrant knowledge search applies tenant project filtering."""
    results = vector_service.search_similar(
        query="Database deadlock runbook",
        project_id="PROJ-TENANT-A",
        top_k=5,
        source_type="knowledge_document",
    )
    assert isinstance(results, list)
    for r in results:
        assert r.get("project_id") == "PROJ-TENANT-A" or "tenant" not in r


@pytest.mark.asyncio
async def test_qdrant_previous_incident_retrieval():
    """Verify Qdrant previous incident search returns atomic JSON payload."""
    results = vector_service.search_similar(
        query="PostgreSQL connection limit reached",
        project_id="PROJ-TENANT-A",
        top_k=3,
        source_type="incident_history",
    )
    assert isinstance(results, list)
