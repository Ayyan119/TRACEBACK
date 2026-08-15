import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class DeploymentModel(Base):
    """SQLAlchemy 2.0 ORM model for Service Deployment Events in TRACEBACK."""

    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique deployment record UUID string",
    )
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to workspace project providing project isolation",
    )
    service_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to microservice target",
    )
    version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Deployment version release tag (e.g. v2.4.1, commit hash)",
    )
    commit_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc="Git commit hash (e.g. 7f3a9b2)",
    )
    author: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="CI/CD Pipeline",
        doc="Engineer or automated system deploying the release",
    )
    deployed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when deployment went live",
    )
    environment: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        default="Production",
        doc="Deployment environment tier (Production, Staging, Development)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="Success",
        doc="Deployment status: Success, Failed, Rolled_Back, In_Progress",
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Release notes or change summary",
    )
    config_changes: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        doc="Environment variables or configuration diff JSON",
    )
    diff_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Code diff summary (e.g. +14 -3 lines in payment_gateway.py)",
    )
    pr_url: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        doc="Pull request / merge request URL",
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
    project = relationship("ProjectModel", lazy="selectin")
    service = relationship("ServiceModel", lazy="selectin")
