"""
Abstract base ORM model shared by all entities.

Provides:
- UUID primary key (uuid.uuid4)
- created_at / updated_at with database-server defaults
- deleted_at + is_deleted for soft-delete pattern
- version for optimistic concurrency control
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TimestampMixin:
    """Mixin that adds server-managed created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin that adds soft-delete capability via a deleted_at timestamp."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        """Return True if this record has been soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark the record as deleted without removing it from the database."""
        self.deleted_at = datetime.now(UTC)


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    Concrete base for all domain models.

    Subclasses inherit:
    - ``id``: UUID primary key
    - ``version``: integer used for optimistic locking (increment on every UPDATE)
    - Timestamp columns (created_at, updated_at)
    - Soft-delete column (deleted_at)
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Optimistic concurrency version counter – incremented on every UPDATE.",
    )

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Return a plain dictionary representation of the model instance."""
        exclude = exclude or set()
        return {
            col.key: getattr(self, col.key)
            for col in self.__table__.columns  # type: ignore[attr-defined]
            if col.key not in exclude
        }
