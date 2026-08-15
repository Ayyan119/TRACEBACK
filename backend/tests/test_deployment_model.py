from datetime import datetime, timezone
import pytest
from app.models.deployment import DeploymentModel
from app.schemas.deployment import (
    DeploymentCreate,
    DeploymentResponse,
    DeploymentStatus,
    DeploymentUpdate,
)


def test_deployment_model_instantiation():
    """Test instantiating DeploymentModel ORM object with foreign keys."""
    dep = DeploymentModel(
        id="dep-123",
        project_id="shopflow",
        service_id="payment-service",
        version="v2.4.1",
        commit_hash="7f3a9b2",
        author="Alex Rivera",
        environment="Production",
        status="Success",
        summary="Updated payment gateway timeout limits",
        config_changes={"MAX_RETRIES": 5, "TIMEOUT_MS": 3000},
        diff_summary="+15 -2 lines in gateway.py",
        pr_url="https://github.com/shopflow/payment-service/pull/42",
    )
    assert dep.id == "dep-123"
    assert dep.project_id == "shopflow"
    assert dep.service_id == "payment-service"
    assert dep.version == "v2.4.1"
    assert dep.commit_hash == "7f3a9b2"
    assert dep.status == "Success"
    assert dep.config_changes["MAX_RETRIES"] == 5


def test_deployment_pydantic_schemas():
    """Test Pydantic request & response schemas for Deployment."""
    # Test Create Schema
    create_dto = DeploymentCreate(
        version="v1.0.9",
        commitHash="a8f3b9c",
        author="ci-bot",
        summary="Automated production build release",
    )
    assert create_dto.version == "v1.0.9"
    assert create_dto.commit_hash == "a8f3b9c"

    # Test Response Schema Serialization & Aliasing
    now = datetime.now(timezone.utc)
    dep_orm = DeploymentModel(
        id="dep-456",
        project_id="shopflow",
        service_id="order-service",
        version="v3.0.0",
        commit_hash="c9b8a7",
        author="Elena Vance",
        deployed_at=now,
        environment="Production",
        status="Success",
        summary="Major release: multi-currency support",
        config_changes={"ENABLE_CURRENCY_CONVERSION": True},
        diff_summary="+140 -20 lines",
        pr_url="https://github.com/shopflow/order-service/pull/101",
        created_at=now,
        updated_at=now,
    )

    response_dto = DeploymentResponse.model_validate(dep_orm)
    dump = response_dto.model_dump(by_alias=True, mode="json")

    assert dump["id"] == "dep-456"
    assert dump["projectId"] == "shopflow"
    assert dump["serviceId"] == "order-service"
    assert dump["commitHash"] == "c9b8a7"
    assert dump["configChanges"]["ENABLE_CURRENCY_CONVERSION"] is True
    assert "deployedAt" in dump
    assert "createdAt" in dump
    assert "updatedAt" in dump
