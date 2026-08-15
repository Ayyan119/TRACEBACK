import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class IncidentHistoryModel(Base):
    """SQLAlchemy 2.0 ORM model for resolved Incident History records in TRACEBACK."""

    __tablename__ = "incident_history"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique incident history record UUID string",
    )
    incident_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        doc="Foreign key to original incident record",
    )
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to workspace project providing project isolation",
    )
    incident_code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        doc="Ticket code (e.g. INC-1001)",
    )
    historical_payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Deterministic JSON representation of the resolved incident",
    )
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc="Qdrant vector point UUID for atomic historical retrieval",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="indexed",
        doc="Indexing status: indexed, pending, failed",
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
    incident = relationship("IncidentModel", backref="history_record", lazy="selectin")
    project = relationship("ProjectModel", backref="incident_histories", lazy="selectin")

    def __repr__(self) -> str:
        return f"<IncidentHistoryModel id={self.id} incident_code={self.incident_code} project_id={self.project_id}>"
