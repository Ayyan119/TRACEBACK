from datetime import datetime, timezone
import pytest
from app.models.incident import IncidentModel
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentSeverity,
    IncidentStatus,
    IncidentUpdate,
)


def test_incident_model_instantiation():
    """Test instantiating IncidentModel ORM object with project_id foreign key."""
    inc = IncidentModel(
        id="inc-1042",
        project_id="shopflow",
        code="INC-1042",
        title="High P95 Latency on Checkout",
        description="Checkout API endpoint P95 latency increased to 3450ms.",
        severity="Critical",
        status="Investigating",
        affected_service="payment-service",
        affected_services=["payment-service", "order-service"],
        confidence=92.5,
        reporter="Datadog Alert",
        environment="Production",
    )
    assert inc.id == "inc-1042"
    assert inc.project_id == "shopflow"
    assert inc.code == "INC-1042"
    assert inc.severity == "Critical"
    assert inc.status == "Investigating"
    assert len(inc.affected_services) == 2


def test_incident_pydantic_schemas():
    """Test Pydantic request & response schemas for Incident."""
    # Test Create Schema
    create_dto = IncidentCreate(
        title="Database Connection Exhaustion",
        description="PostgreSQL connection pool exhausted on payment-service",
        severity=IncidentSeverity.CRITICAL,
        affectedService="payment-service",
        affectedServices=["payment-service"],
        userHypothesis="Recent connection pool config deployment v2.4.1",
    )
    assert create_dto.title == "Database Connection Exhaustion"
    assert create_dto.severity == IncidentSeverity.CRITICAL

    # Test Response Schema Serialization & Aliasing
    now = datetime.now(timezone.utc)
    inc_orm = IncidentModel(
        id="inc-8091",
        project_id="shopflow",
        code="INC-8091",
        title="High Error Rate on Cart API",
        description="Cart checkout endpoints returning HTTP 500 errors",
        severity="High",
        status="Identified",
        affected_service="cart-service",
        affected_services=["cart-service"],
        detected_at=now,
        duration="35m",
        confidence=88.0,
        reporter="SRE On-Call",
        environment="Production",
        root_cause_summary="Memory leak in redis cache connection pool",
        created_at=now,
        updated_at=now,
    )

    response_dto = IncidentResponse.model_validate(inc_orm)
    dump = response_dto.model_dump(by_alias=True, mode="json")

    assert dump["id"] == "inc-8091"
    assert dump["projectId"] == "shopflow"
    assert dump["code"] == "INC-8091"
    assert dump["affectedService"] == "cart-service"
    assert dump["affectedServices"] == ["cart-service"]
    assert dump["rootCauseSummary"] == "Memory leak in redis cache connection pool"
    assert "detectedAt" in dump
    assert "createdAt" in dump
    assert "updatedAt" in dump
