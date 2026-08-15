import pytest
from app.graph.nodes import (
    initialize_state_node,
    process_images_node,
    process_documents_node,
    collect_evidence_node,
    reason_with_tools_node,
    execute_log_tools_node,
    incident_analyzer_node,
)

@pytest.mark.asyncio
async def test_initialize_state_node():
    state = {
        "incident_id": "INC-TEST",
        "project_id": "art-gallary",
        "incident_description": "Database deadlock issue",
    }
    updates = await initialize_state_node(state)
    assert updates["project_id"] == "art-gallary"
    assert "investigation_id" in updates

@pytest.mark.asyncio
async def test_process_images_node():
    state = {
        "incident_images": [
            {"title": "Grafana Error Screenshot", "file_url": "/path/to/error.png"}
        ]
    }
    updates = await process_images_node(state)
    assert len(updates["processed_image_evidence"]) == 1
    assert updates["processed_image_evidence"][0]["relevant"] is True

@pytest.mark.asyncio
async def test_process_documents_node():
    state = {
        "incident_description": "PostgreSQL deadlock timeout",
        "incident_documents": [
            {"name": "Post-Mortem.pdf", "content": "Database pool exhaustion details"}
        ]
    }
    updates = await process_documents_node(state)
    assert len(updates["processed_document_evidence"]) == 1
    assert updates["processed_document_evidence"][0]["relevant"] is True
