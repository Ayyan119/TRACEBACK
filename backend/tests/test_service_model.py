from datetime import datetime, timezone
import pytest
from app.models.project import ProjectModel
from app.models.service import ServiceModel
from app.schemas.service import (
    ServiceCreate,
    ServiceDependency,
    ServiceDeployment,
    ServiceHealth,
    ServiceResponse,
    ServiceType,
)


def test_service_model_instantiation():
    """Test instantiating ServiceModel ORM object with project_id foreign key."""
    service = ServiceModel(
        id="order-service",
        project_id="shopflow",
        name="order-service",
        health="Healthy",
        type="Backend",
        latency_ms=18.5,
        error_rate_percent=0.1,
        dependencies=[{"id": "postgres", "name": "postgres", "type": "database"}],
        recent_deployments=[{"id": "dep-1", "version": "v2.4.1", "deployedAt": "14:00 UTC", "author": "Alex"}],
    )
    assert service.id == "order-service"
    assert service.project_id == "shopflow"
    assert service.name == "order-service"
    assert service.health == "Healthy"
    assert service.latency_ms == 18.5
    assert len(service.dependencies) == 1
    assert len(service.recent_deployments) == 1


def test_service_pydantic_schemas():
    """Test Pydantic request & response schemas for Service."""
    # Test Create Schema
    create_dto = ServiceCreate(
        name="payment-service",
        projectId="shopflow",
        type=ServiceType.BACKEND,
        ownerTeam="Payments Team",
        dependencies=[ServiceDependency(id="redis", name="redis-cluster", type="cache")],
    )
    assert create_dto.name == "payment-service"
    assert create_dto.project_id == "shopflow"
    assert create_dto.type == ServiceType.BACKEND
    assert len(create_dto.dependencies) == 1

    # Test Response Schema Serialization & Aliasing
    now = datetime.now(timezone.utc)
    service_orm = ServiceModel(
        id="payment-service",
        project_id="shopflow",
        name="payment-service",
        health="Degraded",
        type="Backend",
        latency_ms=3500.0,
        error_rate_percent=12.4,
        recent_incidents_count=1,
        dependencies=[{"id": "pg", "name": "postgres", "type": "database"}],
        recent_deployments=[{"id": "d-1", "version": "v1.2", "deployedAt": "12:00 UTC", "author": "Elena"}],
        owner_team="Payments Team",
        repository_url="https://github.com/shopflow/payment-service",
        environment="Production",
        created_at=now,
        updated_at=now,
    )

    response_dto = ServiceResponse.model_validate(service_orm)
    dump = response_dto.model_dump(by_alias=True)

    assert dump["id"] == "payment-service"
    assert dump["projectId"] == "shopflow"
    assert dump["latencyMs"] == 3500.0
    assert dump["errorRatePercent"] == 12.4
    assert dump["recentIncidentsCount"] == 1
    assert dump["ownerTeam"] == "Payments Team"
    assert "createdAt" in dump
    assert "updatedAt" in dump
