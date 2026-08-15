import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class EvidenceModel(Base):
    """SQLAlchemy 2.0 ORM model for Investigation Evidence Items in TRACEBACK."""

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique evidence item UUID string",
    )
    incident_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to target incident",
    )
    type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="Evidence type: log, screenshot, metric, stack_trace, deployment, document",
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Human readable evidence title or snippet header",
    )
    source: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="User Upload",
        doc="Evidence origin source: Datadog, Prometheus, Manual Upload, System Log",
    )
    file_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        doc="Storage file URL or relative download path",
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="File size in bytes",
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="MIME type (e.g. application/pdf, text/plain, image/png)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="ready",
        doc="Upload/processing status: selected, uploading, uploaded, processing, ready, failed",
    )
    raw_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Raw inline log text, stack trace snippet, or document content",
    )
    metadata_json: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        doc="Parsed telemetry metadata or chunking details",
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
    incident = relationship("IncidentModel", backref="evidence_items", lazy="selectin")
