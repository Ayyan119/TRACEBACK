import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class InvestigationModel(Base):
    """SQLAlchemy 2.0 ORM model for persistent AI Investigation Runs in TRACEBACK."""

    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique investigation run UUID string",
    )
    incident_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to target incident",
    )
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to workspace project providing project isolation",
    )
    investigation_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        doc="Sequential run number for the incident (1, 2, 3...)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="CREATED",
        doc="Lifecycle status: CREATED, RUNNING, COMPLETED, FAILED, CANCELLED",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when investigation run started",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when investigation run finished",
    )
    duration_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Total execution duration in milliseconds",
    )
    incident_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Incident symptom description at time of run",
    )
    final_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Executive summary statement from agent RCA",
    )
    root_cause: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Primary root cause title or explanation",
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Root cause confidence score (0-100)",
    )
    final_report_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Complete structured RCA final report payload",
    )
    selected_hypothesis_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Primary accepted root cause hypothesis payload",
    )
    hypotheses_json: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        doc="List of all candidate hypotheses evaluated",
    )
    accepted_evidence_json: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        doc="List of accepted evidence items",
    )
    rejected_evidence_json: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        doc="List of rejected evidence items with rejection reasons",
    )
    execution_trace_json: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        doc="List of node execution trace steps (durations, nodes, details)",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Sanitized error message if status is FAILED",
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

    # Relationships
    incident = relationship("IncidentModel", backref="investigation_runs", lazy="selectin")
    project = relationship("ProjectModel", backref="investigations", lazy="selectin")

    def __repr__(self) -> str:
        return f"<InvestigationModel id={self.id} incident_id={self.incident_id} run=#{self.investigation_number} status={self.status}>"
