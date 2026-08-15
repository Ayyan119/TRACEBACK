import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class KnowledgeDocumentModel(Base):
    """SQLAlchemy 2.0 ORM model for Workspace Knowledge Base Documents in TRACEBACK."""

    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique knowledge document UUID string",
    )
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to target workspace project",
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Document title or original filename",
    )
    category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="Architecture",
        doc="Document category: Architecture, Runbook, API Spec, Postmortem, Incident Log, Configuration",
    )
    file_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        doc="Relative or cloud storage file URL",
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Document file size in bytes",
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="MIME type (e.g. application/pdf, text/markdown, application/json)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="ready",
        doc="Vector indexing status: pending, chunking, indexed, failed, ready",
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of text chunks embedded in vector database",
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Extracted full text content for RAG search",
    )
    metadata_json: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        doc="Document metadata or tag key-values",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    project = relationship("ProjectModel", backref="knowledge_documents", lazy="selectin")
