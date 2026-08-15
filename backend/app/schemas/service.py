from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ServiceHealth(str, Enum):
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


class ServiceType(str, Enum):
    API = "API"
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    WORKER = "Worker"
    DATABASE = "Database"
    CACHE = "Cache"
    QUEUE = "Queue"
    OTHER = "Other"


class ServiceDependency(BaseModel):
    id: str
    name: str
    type: str = "internal"  # 'internal' | 'external' | 'database' | 'cache'

    model_config = ConfigDict(from_attributes=True)


class ServiceDeployment(BaseModel):
    id: str
    version: str
    deployed_at: str = Field(..., alias="deployedAt")
    author: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=128, description="Service name")
    type: Optional[ServiceType] = Field(ServiceType.BACKEND, description="Service tier type")
    description: Optional[str] = Field(None, max_length=1000, description="Service overview")
    owner_team: Optional[str] = Field(None, max_length=128, alias="ownerTeam", description="Owner engineering team")
    repository_url: Optional[str] = Field(None, max_length=256, alias="repositoryUrl", description="Git repository URL")
    environment: Optional[str] = Field("Production", max_length=32, description="Deployment environment")


class ServiceCreate(ServiceBase):
    project_id: Optional[str] = Field(None, alias="projectId", description="Target workspace project ID")
    dependencies: Optional[List[ServiceDependency]] = Field(default_factory=list)
    recent_deployments: Optional[List[ServiceDeployment]] = Field(default_factory=list, alias="recentDeployments")


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=128)
    health: Optional[ServiceHealth] = None
    type: Optional[ServiceType] = None
    description: Optional[str] = None
    latency_ms: Optional[float] = Field(None, alias="latencyMs")
    error_rate_percent: Optional[float] = Field(None, alias="errorRatePercent")
    owner_team: Optional[str] = Field(None, alias="ownerTeam")
    repository_url: Optional[str] = Field(None, alias="repositoryUrl")
    environment: Optional[str] = None


class ServiceResponse(ServiceBase):
    id: str
    project_id: str = Field(..., alias="projectId")
    health: ServiceHealth = ServiceHealth.HEALTHY
    latency_ms: float = Field(15.0, alias="latencyMs")
    error_rate_percent: float = Field(0.0, alias="errorRatePercent")
    recent_incidents_count: int = Field(0, alias="recentIncidentsCount")
    dependencies: List[ServiceDependency] = Field(default_factory=list)
    recent_deployments: List[ServiceDeployment] = Field(default_factory=list, alias="recentDeployments")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
