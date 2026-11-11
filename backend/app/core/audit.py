"""
Audit event creation helpers.

This module provides the canonical interface for recording audit events.
Every privileged action in SystemaOps must call ``create_audit_event``
so that the audit trail is complete and auditor-readable.

Design principles
-----------------
- Audit events are fire-and-forget from the caller's perspective.
- If audit event creation fails, the primary operation is NOT rolled back.
  We prefer a successful user-facing operation with a missing audit event
  over a failed operation with a complete audit event. This is logged at
  ERROR level for follow-up.
- Events are written to the same database session as the primary operation
  so they share the same transaction (and thus commit atomically).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent

if TYPE_CHECKING:
    from starlette.requests import Request

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Well-known action tokens
# ---------------------------------------------------------------------------
# Keep these as module-level constants so callers get IDE completion and
# typos are caught at import time rather than at runtime.

class AuditAction:
    # Auth
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGIN_FAILED = "USER_LOGIN_FAILED"
    USER_LOGOUT = "USER_LOGOUT"
    USER_PASSWORD_RESET_REQUESTED = "USER_PASSWORD_RESET_REQUESTED"
    USER_PASSWORD_RESET_COMPLETED = "USER_PASSWORD_RESET_COMPLETED"
    USER_EMAIL_VERIFIED = "USER_EMAIL_VERIFIED"
    USER_ACCOUNT_LOCKED = "USER_ACCOUNT_LOCKED"

    # Organization
    ORGANIZATION_CREATED = "ORGANIZATION_CREATED"
    ORGANIZATION_UPDATED = "ORGANIZATION_UPDATED"
    ORGANIZATION_SUSPENDED = "ORGANIZATION_SUSPENDED"
    MEMBER_INVITED = "MEMBER_INVITED"
    MEMBER_JOINED = "MEMBER_JOINED"
    MEMBER_ROLE_CHANGED = "MEMBER_ROLE_CHANGED"
    MEMBER_REMOVED = "MEMBER_REMOVED"

    # AI Systems
    AI_SYSTEM_CREATED = "AI_SYSTEM_CREATED"
    AI_SYSTEM_UPDATED = "AI_SYSTEM_UPDATED"
    AI_SYSTEM_DELETED = "AI_SYSTEM_DELETED"
    AI_SYSTEM_STATUS_CHANGED = "AI_SYSTEM_STATUS_CHANGED"
    AI_SYSTEM_RISK_CLASSIFIED = "AI_SYSTEM_RISK_CLASSIFIED"

    # Assessments
    ASSESSMENT_CREATED = "ASSESSMENT_CREATED"
    ASSESSMENT_SUBMITTED = "ASSESSMENT_SUBMITTED"
    ASSESSMENT_APPROVED = "ASSESSMENT_APPROVED"
    ASSESSMENT_REJECTED = "ASSESSMENT_REJECTED"

    # Evidence
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EVIDENCE_REVIEWED = "EVIDENCE_REVIEWED"
    EVIDENCE_INVALIDATED = "EVIDENCE_INVALIDATED"
    EVIDENCE_DELETED = "EVIDENCE_DELETED"

    # Incidents
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_UPDATED = "INCIDENT_UPDATED"
    INCIDENT_RESOLVED = "INCIDENT_RESOLVED"
    INCIDENT_CLOSED = "INCIDENT_CLOSED"

    # Vendors
    VENDOR_CREATED = "VENDOR_CREATED"
    VENDOR_UPDATED = "VENDOR_UPDATED"
    VENDOR_REVIEWED = "VENDOR_REVIEWED"

    # Contracts
    CONTRACT_CREATED = "CONTRACT_CREATED"
    CONTRACT_REVIEWED = "CONTRACT_REVIEWED"
    CONTRACT_APPROVED = "CONTRACT_APPROVED"

    # Training
    TRAINING_ASSIGNED = "TRAINING_ASSIGNED"
    TRAINING_COMPLETED = "TRAINING_COMPLETED"

    # Approvals
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_REJECTED = "APPROVAL_REJECTED"

    # Regulatory
    REGULATORY_VERSION_UPDATED = "REGULATORY_VERSION_UPDATED"


async def create_audit_event(
    db: AsyncSession,
    action: str,
    actor_id: UUID | None = None,
    actor_email: str | None = None,
    organization_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: UUID | None = None,
    correlation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    request: "Request | None" = None,
) -> AuditEvent:
    """
    Persist an audit event to the database.

    Parameters
    ----------
    db:
        The active async database session (shares the caller's transaction).
    action:
        Event type token from ``AuditAction`` constants.
    actor_id:
        UUID of the user who performed the action. ``None`` for system actions.
    actor_email:
        Denormalised email for permanent audit trail.
    organization_id:
        Tenant scope. ``None`` for platform-level events.
    resource_type:
        E.g. ``"ai_system"``, ``"evidence"``, ``"incident"``.
    resource_id:
        Primary key of the affected resource.
    correlation_id:
        Links events from the same logical operation or HTTP request.
    metadata:
        Arbitrary contextual key-value pairs (old/new values, reason, etc.).
    request:
        Optional Starlette request for extracting IP address and user-agent.

    Returns
    -------
    AuditEvent
        The newly created (but not yet committed) audit event instance.
    """
    ip_address: str | None = None
    user_agent: str | None = None

    if request is not None:
        # Respect X-Forwarded-For from trusted load balancers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        else:
            ip_address = getattr(request.client, "host", None)
        user_agent = request.headers.get("User-Agent")

    event = AuditEvent(
        action=action,
        actor_id=actor_id,
        actor_email=actor_email,
        organization_id=organization_id,
        resource_type=resource_type,
        resource_id=resource_id,
        correlation_id=correlation_id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata or {},
    )
    db.add(event)

    logger.debug(
        "audit_event_created",
        extra={
            "action": action,
            "actor_id": str(actor_id) if actor_id else None,
            "organization_id": str(organization_id) if organization_id else None,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
        },
    )

    return event
