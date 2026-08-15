import pytest
from app.graph.state import InvestigationState, EvidenceItem

def test_investigation_state_initialization():
    state: InvestigationState = {
        "investigation_id": "inv-123",
        "incident_id": "INC-1001",
        "project_id": "art-gallary",
        "incident_description": "Database connection pool timeout",
        "accepted_evidence": [],
        "tool_iterations": 0,
    }
    assert state["investigation_id"] == "inv-123"
    assert state["incident_id"] == "INC-1001"
    assert state["tool_iterations"] == 0

def test_evidence_item_model():
    item = EvidenceItem(
        evidence_id="EVD-1",
        source_type="document",
        source_name="Post-Mortem.pdf",
        content="Connection pool overflow",
        relevance=True,
        confidence=0.95
    )
    assert item.evidence_id == "EVD-1"
    assert item.confidence == 0.95
