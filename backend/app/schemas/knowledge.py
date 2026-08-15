from datetime import datetime
from typing import Any, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class KnowledgeDocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256, description="Document title or header")
    category: str = Field("Architecture", max_length=64, description="Document category tag")
    content: Optional[str] = Field(None, description="Full text content or extracted summary")
    metadata_json: Optional[Any] = Field(
        default_factory=dict,
        serialization_alias="metadata",
        validation_alias=AliasChoices("metadata_json", "metadata"),
        description="Custom document metadata dict",
    )


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    project_id: Optional[str] = Field(None, alias="projectId", description="Target project ID (inferred from URL path if omitted)")


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    id: str
    project_id: str = Field(..., alias="projectId")
    file_url: Optional[str] = Field(None, alias="fileUrl")
    file_size: Optional[int] = Field(None, alias="fileSize")
    mime_type: Optional[str] = Field(None, alias="mimeType")
    status: str = "ready"
    chunk_count: int = Field(0, alias="chunkCount")
    created_at: datetime = Field(
        ...,
        serialization_alias="createdAt",
        validation_alias=AliasChoices("created_at", "createdAt"),
    )
    updated_at: datetime = Field(
        ...,
        serialization_alias="updatedAt",
        validation_alias=AliasChoices("updated_at", "updatedAt"),
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
