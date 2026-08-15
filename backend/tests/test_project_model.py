from datetime import datetime, timezone
import pytest
from app.models.project import ProjectModel
from app.schemas.project import EnvironmentTier, ProjectCreate, ProjectResponse, ProjectUpdate


def test_project_model_instantiation():
    """Test instantiating ProjectModel ORM object."""
    proj = ProjectModel(
        id="shopflow",
        name="ShopFlow",
        slug="shopflow",
        description="Main e-commerce checkout pipeline",
        environment="production",
        service_count=6,
        active_incident_count=1,
    )
    assert proj.id == "shopflow"
    assert proj.name == "ShopFlow"
    assert proj.slug == "shopflow"
    assert proj.service_count == 6
    assert proj.active_incident_count == 1
    assert proj.environment == "production"


def test_project_pydantic_schemas():
    """Test Pydantic request & response schemas for Project."""
    # Test Create
    create_dto = ProjectCreate(
        name="FinBank",
        slug="finbank",
        description="Core financial ledger",
        environment=EnvironmentTier.PRODUCTION,
        owner_team="Core Ledger Team",
    )
    assert create_dto.name == "FinBank"
    assert create_dto.slug == "finbank"
    assert create_dto.environment == EnvironmentTier.PRODUCTION

    # Test Response Schema Serialization & Aliasing
    now = datetime.now(timezone.utc)
    proj_orm = ProjectModel(
        id="finbank",
        name="FinBank",
        slug="finbank",
        description="Core financial ledger",
        environment="production",
        service_count=4,
        active_incident_count=0,
        owner_team="Core Ledger Team",
        repository_url="https://github.com/finbank/ledger",
        created_at=now,
        updated_at=now,
    )

    response_dto = ProjectResponse.model_validate(proj_orm)
    dump = response_dto.model_dump(by_alias=True)

    assert dump["id"] == "finbank"
    assert dump["name"] == "FinBank"
    assert dump["serviceCount"] == 4
    assert dump["activeIncidentCount"] == 0
    assert "createdAt" in dump
    assert "updatedAt" in dump
