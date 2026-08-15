from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class EnvironmentTier(str, Enum):
    """Supported deployment environment tiers."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


class ProjectBase(BaseModel):
    """Base fields shared across project request and response schemas."""
    name: str = Field(..., min_length=2, max_length=128, description="Project workspace name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    environment: EnvironmentTier = Field(EnvironmentTier.PRODUCTION, description="Environment tier")
    owner_team: Optional[str] = Field(None, max_length=128, alias="ownerTeam", description="Owner engineering team")
    repository_url: Optional[str] = Field(None, max_length=256, alias="repositoryUrl", description="Git repository URL")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ProjectCreate(ProjectBase):
    """Schema for creating a new workspace project."""
    slug: Optional[str] = Field(None, min_length=2, max_length=128, pattern="^[a-z0-9-]+$", description="URL-friendly slug (auto-generated if omitted)")


class ProjectUpdate(BaseModel):
    """Schema for updating an existing workspace project (partial update)."""
    name: Optional[str] = Field(None, min_length=2, max_length=128)
    description: Optional[str] = Field(None, max_length=1000)
    environment: Optional[EnvironmentTier] = None
    owner_team: Optional[str] = None
    repository_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project API responses (matching frontend types/project.ts)."""
    id: str
    slug: str
    service_count: int = Field(0, alias="serviceCount")
    active_incident_count: int = Field(0, alias="activeIncidentCount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
