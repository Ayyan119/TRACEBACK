from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class DeploymentStatus(str, Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    ROLLED_BACK = "Rolled_Back"
    IN_PROGRESS = "In_Progress"


class DeploymentBase(BaseModel):
    version: str = Field(..., min_length=1, max_length=64, description="Release version string (e.g. v2.4.1)")
    commit_hash: Optional[str] = Field(None, alias="commitHash", max_length=64, description="Git commit SHA hash")
    author: str = Field("CI/CD Pipeline", max_length=128, description="Deployer username or service account")
    environment: Optional[str] = Field("Production", max_length=32, description="Deployment environment tier")
    status: DeploymentStatus = Field(DeploymentStatus.SUCCESS, description="Deployment outcome status")
    summary: Optional[str] = Field(None, max_length=2000, description="Release summary or changelog")
    config_changes: Optional[Any] = Field(None, alias="configChanges", description="Config diff JSON or dict")
    diff_summary: Optional[str] = Field(None, alias="diffSummary", description="Git diff summary stats")
    pr_url: Optional[str] = Field(None, alias="prUrl", max_length=256, description="Git pull request URL")


class DeploymentCreate(DeploymentBase):
    project_id: Optional[str] = Field(None, alias="projectId", description="Parent project ID (inferred from path if omitted)")
    service_id: Optional[str] = Field(None, alias="serviceId", description="Target service ID (inferred from path if omitted)")
    deployed_at: Optional[datetime] = Field(None, alias="deployedAt", description="Timestamp when deployment took place")


class DeploymentUpdate(BaseModel):
    status: Optional[DeploymentStatus] = None
    summary: Optional[str] = Field(None, max_length=2000)
    config_changes: Optional[Any] = Field(None, alias="configChanges")
    diff_summary: Optional[str] = Field(None, alias="diffSummary")
    pr_url: Optional[str] = Field(None, alias="prUrl")


class DeploymentResponse(DeploymentBase):
    id: str
    project_id: str = Field(..., alias="projectId")
    service_id: str = Field(..., alias="serviceId")
    deployed_at: datetime = Field(..., alias="deployedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
