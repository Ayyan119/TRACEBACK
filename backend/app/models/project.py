import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ProjectModel(Base):
    """SQLAlchemy 2.0 ORM model for TRACEBACK Workspace Projects."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique project identifier (UUID string or human slug)",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="Human readable name of the project",
    )
    slug: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        doc="URL-friendly unique project slug",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Optional description of the project workspace",
    )
    environment: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="production",
        doc="Environment tier: production, staging, or development",
    )
    service_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Cached count of active microservices in this project",
    )
    active_incident_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Cached count of open/investigating incidents in this project",
    )
    owner_team: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        doc="Engineering team or owner group",
    )
    repository_url: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        doc="Git repository URL for source code context",
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
