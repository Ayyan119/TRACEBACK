import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ServiceModel(Base):
    """SQLAlchemy 2.0 ORM model for TRACEBACK Microservices isolated by project_id."""

    __tablename__ = "services"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique service identifier (UUID string or service slug)",
    )
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to workspace project providing strict project isolation",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="Service name (e.g. order-service, payment-service)",
    )
    health: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="Healthy",
        doc="Service operational health: Healthy, Degraded, Critical, Unknown",
    )
    type: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        default="Backend",
        doc="Service tier type: API, Frontend, Backend, Worker, Database, Cache, Queue, Other",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Service functionality overview",
    )
    latency_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        default=None,
        nullable=True,
        doc="P95 latency in milliseconds",
    )
    error_rate_percent: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="HTTP/gRPC error rate percentage",
    )
    recent_incidents_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Count of recent incidents involving this service",
    )
    dependencies: Mapped[List[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="JSON list of service dependencies",
    )
    recent_deployments: Mapped[List[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="JSON list of recent service deployments",
    )
    owner_team: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Owner engineering team",
    )
    repository_url: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        doc="Git repository URL",
    )
    environment: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        default="Production",
        doc="Deployment environment",
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
    project = relationship("ProjectModel", backref="services", lazy="selectin")
