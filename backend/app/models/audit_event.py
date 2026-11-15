"""
AuditEvent model — append-only compliance audit log.

Every privileged action in SystemaOps generates an AuditEvent. These records
are never updated or soft-deleted; they are permanent and immutable from the
application's perspective. Database-level INSERT-only policies should be
applied in production.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditEvent(Base):
    """
    Immutable audit log entry.

    Design notes
    ------------
    - No ``updated_at``, ``deleted_at``, or ``version`` columns — records are
      append-only to maintain integrity.
    - ``actor_email`` is denormalised so the log remains accurate even if the
      user record is later deleted or anonymised.
    - ``correlation_id`` links events from the same logical operation
      (e.g. all events triggered by a single API request).
    - ``metadata`` is an open JSONB object for contextual key-value pairs.
    """

    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_organization_id", "organization_id"),
        Index("ix_audit_events_actor_id", "actor_id"),
        Index("ix_audit_events_action", "action"),
        Index("ix_audit_events_resource_type_id", "resource_type", "resource_id"),
        Index("ix_audit_events_created_at", "created_at"),
        Index("ix_audit_events_correlation_id", "correlation_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=True,
        comment="NULL for platform-level events (e.g. new org created).",
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=True,
        comment="User who performed the action. NULL for system/scheduler.",
    )
    actor_email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
        comment="Denormalised email for permanent audit trail.",
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Event type token, e.g. AI_SYSTEM_CREATED.",
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Type of the affected resource, e.g. ai_system.",
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=True,
        comment="PK of the affected resource.",
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Links events from the same logical operation / request.",
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Free-form contextual data (old_value, new_value, reason, …).",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuditEvent id={self.id} action={self.action!r}>"
