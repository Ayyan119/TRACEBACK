import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class IncidentModel(Base):
    """SQLAlchemy 2.0 ORM model for TRACEBACK Incidents isolated by project_id."""

    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique incident identifier (UUID string)",
    )
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to workspace project providing strict project isolation",
    )
    code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        doc="Human readable incident ticket code (e.g. INC-1042)",
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Short incident title describing problem statement",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed description or initial report",
    )
    severity: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="High",
        doc="Incident severity: Critical, High, Medium, Low",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="Investigating",
        doc="Incident lifecycle status: Investigating, Identified, Monitoring, Resolved",
    )
    affected_service: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Primary affected service name or ID",
    )
    affected_services: Mapped[List[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="JSON list of all impacted service names",
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when anomaly or outage was detected",
    )
    duration: Mapped[str] = mapped_column(
        String(64),
        default="Active",
        nullable=False,
        doc="Incident duration string (e.g. Active, 45m, 2h 15m)",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        default=85.0,
        nullable=False,
        doc="AI root-cause confidence score percentage (0-100)",
    )
    reporter: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        default="SRE On-Call",
        doc="Reporter or triggering monitor/alerting rule",
    )
    environment: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        default="Production",
        doc="Deployment environment",
    )
    root_cause_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="AI synthesized root cause summary",
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when incident reached Resolved status",
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

    # Relationship back to project
    project = relationship("ProjectModel", backref="incidents", lazy="selectin")
