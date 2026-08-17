import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class UserModel(Base):
    """SQLAlchemy 2.0 ORM model for TRACEBACK User Identities."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"usr_{uuid.uuid4().hex[:12]}",
        doc="Unique internal user identifier (e.g., usr_123456789abc)",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="Display name of the engineer/user (e.g. Ayyan Shahid)",
    )
    role: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="Senior Software Engineer",
        doc="Technical role (e.g. AI Engineer, Senior SRE)",
    )
    encrypted_openai_api_key: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Fernet encrypted OpenAI API key",
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
