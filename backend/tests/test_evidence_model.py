from datetime import datetime, timezone
import pytest
from app.models.evidence import EvidenceModel
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceType,
    EvidenceUploadStatus,
)


def test_evidence_model_instantiation():
    """Test instantiating EvidenceModel ORM object with incident_id foreign key."""
    ev = EvidenceModel(
        id="ev-101",
        incident_id="inc-1042",
        type="log",
        title="Application Server Stack Trace",
        source="Datadog APM",
        file_url="/uploads/stacktrace.log",
        file_size=4096,
        mime_type="text/plain",
        status="ready",
        raw_content="Exception in thread main java.lang.NullPointerException at com.shopflow.PaymentProcessor.charge(PaymentProcessor.java:142)",
        metadata_json={"host": "api-pod-8", "env": "prod"},
    )
    assert ev.id == "ev-101"
    assert ev.incident_id == "inc-1042"
    assert ev.type == "log"
    assert ev.file_size == 4096
    assert ev.metadata_json["host"] == "api-pod-8"


def test_evidence_pydantic_schemas():
    """Test Pydantic request & response schemas for Evidence."""
    # Test Create Schema
    create_dto = EvidenceCreate(
        type=EvidenceType.STACK_TRACE,
        title="Payment Gateway Timeout Log",
        source="Manual Upload",
        rawContent="ERROR 504 Gateway Timeout: connection refused",
    )
    assert create_dto.type == EvidenceType.STACK_TRACE
    assert create_dto.title == "Payment Gateway Timeout Log"

    # Test Response Schema Serialization & Aliasing
    now = datetime.now(timezone.utc)
    ev_orm = EvidenceModel(
        id="ev-202",
        incident_id="inc-1042",
        type="screenshot",
        title="Grafana Dashboard Spike",
        source="Grafana",
        file_url="/uploads/dashboard.png",
        file_size=1048576,
        mime_type="image/png",
        status="ready",
        metadata_json={"dashboard": "Checkout Latency"},
        created_at=now,
        updated_at=now,
    )

    response_dto = EvidenceResponse.model_validate(ev_orm)
    dump = response_dto.model_dump(by_alias=True, mode="json")

    assert dump["id"] == "ev-202"
    assert dump["incidentId"] == "inc-1042"
    assert dump["type"] == "screenshot"
    assert dump["fileUrl"] == "/uploads/dashboard.png"
    assert dump["fileSize"] == 1048576
    assert dump["mimeType"] == "image/png"
    assert "uploadedAt" in dump
