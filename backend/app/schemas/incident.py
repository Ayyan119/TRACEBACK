from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from app.core.utils import count_words


class IncidentSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentStatus(str, Enum):
    INVESTIGATING = "Investigating"
    IDENTIFIED = "Identified"
    MONITORING = "Monitoring"
    RESOLVED = "Resolved"


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=256, description="Incident summary title")
    description: str = Field(..., min_length=1, description="Detailed problem description or report")
    severity: IncidentSeverity = Field(IncidentSeverity.HIGH, description="Incident severity level")
    affected_service: Optional[str] = Field("Backend", alias="affectedService", description="Primary affected service")
    affected_services: Optional[List[str]] = Field(default_factory=list, alias="affectedServices", description="List of affected service names")
    reporter: Optional[str] = Field("SRE On-Call", max_length=128, description="Reporter or trigger source")
    environment: Optional[str] = Field("Production", max_length=32, description="Environment tier")

    @field_validator("description")
    @classmethod
    def validate_description_word_count(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Incident description is required.")
        words = count_words(v)
        if words > 2000:
            raise ValueError("Incident description cannot exceed 2,000 words.")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class IncidentCreate(IncidentBase):
    project_id: Optional[str] = Field(None, alias="projectId", description="Parent project ID (inferred from path if omitted)")
    detected_at: Optional[datetime] = Field(None, alias="detectedAt", description="Timestamp when outage was detected")
    user_hypothesis: Optional[str] = Field(None, alias="userHypothesis", description="Initial user hypothesis")


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=256)
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    affected_service: Optional[str] = Field(None, alias="affectedService")
    affected_services: Optional[List[str]] = Field(None, alias="affectedServices")
    duration: Optional[str] = None
    confidence: Optional[float] = None
    root_cause_summary: Optional[str] = Field(
        None,
        serialization_alias="rootCauseSummary",
        validation_alias=AliasChoices("root_cause_summary", "rootCauseSummary"),
    )
    environment: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class IncidentResponse(IncidentBase):
    id: str
    project_id: str = Field(..., alias="projectId")
    code: str
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    detected_at: datetime = Field(..., alias="detectedAt")
    duration: str = "Active"
    confidence: float = 85.0
    root_cause_summary: Optional[str] = Field(
        None,
        serialization_alias="rootCauseSummary",
        validation_alias=AliasChoices("root_cause_summary", "rootCauseSummary"),
    )
    resolved_at: Optional[datetime] = Field(None, alias="resolvedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
