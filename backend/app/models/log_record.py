import uuid
from datetime import datetime, timezone, date, time
from typing import Any, Dict, Optional
from sqlalchemy import String, Text, DateTime, Date, Time, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class LogRecordModel(Base):
    """SQLAlchemy model for structured log storage (Knowledge & Incident logs)."""

    __tablename__ = "log_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    incident_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    file_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(
        Date,
        default=lambda: datetime.now(timezone.utc).date(),
        nullable=False,
        index=True,
    )
    time: Mapped[time] = mapped_column(
        Time,
        default=lambda: datetime.now(timezone.utc).time(),
        nullable=False,
    )
    day: Mapped[str] = mapped_column(
        String(20),
        default=lambda: datetime.now(timezone.utc).strftime("%A"),
        nullable=False,
        index=True,
    )

    log_type: Mapped[str] = mapped_column(
        String(50),
        default="application",
        nullable=False,
        index=True,
    )
    level: Mapped[str] = mapped_column(
        String(20),
        default="INFO",
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    service: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    raw_line: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    parse_status: Mapped[str] = mapped_column(
        String(20),
        default="parsed",
        nullable=False,
        index=True,
    )
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project = relationship("ProjectModel", backref="log_records")
    incident = relationship("IncidentModel", backref="log_records")

    def __repr__(self) -> str:
        return f"<LogRecordModel id={self.id} level={self.level} service={self.service}>"
