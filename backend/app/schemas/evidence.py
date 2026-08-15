from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class EvidenceType(str, Enum):
    LOG = "log"
    SCREENSHOT = "screenshot"
    METRIC = "metric"
    STACK_TRACE = "stack_trace"
    DEPLOYMENT = "deployment"
    DOCUMENT = "document"


class EvidenceUploadStatus(str, Enum):
    SELECTED = "selected"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class EvidenceBase(BaseModel):
    type: EvidenceType = Field(EvidenceType.LOG, description="Evidence category")
    title: str = Field(..., min_length=1, max_length=256, description="Evidence title or header")
    source: str = Field("User Upload", max_length=128, description="Evidence origin source")
    raw_content: Optional[str] = Field(None, alias="rawContent", description="Raw log or stack trace text")
    metadata_json: Optional[Any] = Field(
        default_factory=dict,
        serialization_alias="metadata",
        validation_alias=AliasChoices("metadata_json", "metadata"),
        description="Custom metadata dict",
    )


class EvidenceCreate(EvidenceBase):
    incident_id: Optional[str] = Field(None, alias="incidentId", description="Target incident ID (inferred from URL path if omitted)")


class EvidenceResponse(EvidenceBase):
    id: str
    incident_id: str = Field(..., alias="incidentId")
    file_url: Optional[str] = Field(None, alias="fileUrl")
    file_size: Optional[int] = Field(None, alias="fileSize")
    mime_type: Optional[str] = Field(None, alias="mimeType")
    status: EvidenceUploadStatus = EvidenceUploadStatus.READY
    uploaded_at: datetime = Field(
        ...,
        serialization_alias="uploadedAt",
        validation_alias=AliasChoices("uploaded_at", "created_at", "uploadedAt"),
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
