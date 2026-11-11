"""Organization and audit endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.audit_event import AuditEvent
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse
from app.schemas.common import PaginatedResponse

organizations_router = APIRouter()
audit_router = APIRouter()


@organizations_router.get("/organizations/{org_slug}", response_model=OrganizationResponse)
async def get_organization(
    org_slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    result = await db.execute(
        select(Organization).where(
            Organization.slug == org_slug,
            Organization.deleted_at.is_(None),
        )
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=404, detail="Organisation not found.")
    return OrganizationResponse.model_validate(org)


@audit_router.get("/organizations/{org_slug}/audit/events")
async def list_audit_events(
    org_slug: str,
    page: int = 1,
    page_size: int = 50,
    action: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List audit events for an organisation (auditors/admins only)."""
    org_result = await db.execute(
        select(Organization).where(Organization.slug == org_slug, Organization.deleted_at.is_(None))
    )
    org = org_result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=404, detail="Organisation not found.")

    stmt = select(AuditEvent).where(AuditEvent.organization_id == org.id)
    if action:
        stmt = stmt.where(AuditEvent.action == action)

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    stmt = stmt.order_by(AuditEvent.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    events = result.scalars().all()

    return {
        "items": [
            {
                "id": str(e.id),
                "action": e.action,
                "actor_email": e.actor_email,
                "resource_type": e.resource_type,
                "resource_id": str(e.resource_id) if e.resource_id else None,
                "metadata": e.metadata,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
