import pytest
from app.analysis.evidence import analyze_incident_document

@pytest.mark.asyncio
async def test_analyze_incident_document_relevant():
    doc = {
        "name": "Database Lock Contention Notes.docx",
        "content": "PostgreSQL connection pool max_connections timeout error log trace."
    }
    analysis = await analyze_incident_document(doc, "Database pool timeout")
    assert analysis.relevant is True
    assert analysis.confidence >= 0.70
    assert len(analysis.error_signatures) > 0

@pytest.mark.asyncio
async def test_analyze_incident_document_irrelevant():
    doc = {
        "name": "Lunch Menu.pdf",
        "content": "Friday pizza party menu options."
    }
    analysis = await analyze_incident_document(doc, "Database pool timeout")
    assert analysis.relevant is False
