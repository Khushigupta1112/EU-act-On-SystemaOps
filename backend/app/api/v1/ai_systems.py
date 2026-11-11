"""
AI Systems CRUD API.

GET    /api/v1/organizations/{org_slug}/ai-systems
POST   /api/v1/organizations/{org_slug}/ai-systems
GET    /api/v1/organizations/{org_slug}/ai-systems/{id}
PATCH  /api/v1/organizations/{org_slug}/ai-systems/{id}
DELETE /api/v1/organizations/{org_slug}/ai-systems/{id}
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, create_audit_event
from app.database import get_db
from app.dependencies import get_current_user, get_org_member_dependency, require_permission
from app.models.ai_system import AISystem
from app.models.organization import Organization, OrganizationMember
from app.models.role import Permission
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.ai_system import AISystemCreate, AISystemResponse, AISystemUpdate
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)
router = APIRouter()

_get_member = get_org_member_dependency()


async def _get_org_by_slug(slug: str, db: AsyncSession) -> Organization:
    result = await db.execute(
        select(Organization).where(
            Organization.slug == slug, Organization.deleted_at.is_(None)
        )
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=404, detail="Organisation not found.")
    return org


@router.get("/organizations/{org_slug}/ai-systems", response_model=PaginatedResponse[AISystemResponse])
async def list_ai_systems(
    org_slug: str,
    page: int = 1,
    page_size: int = 25,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AISystemResponse]:
    """List all AI systems for the organisation (paginated)."""
    org = await _get_org_by_slug(org_slug, db)
    repo = BaseRepository(AISystem, db)
    items, total = await repo.list(
        organization_id=org.id,
        skip=(page - 1) * page_size,
        limit=page_size,
    )
    return PaginatedResponse.create(
        items=[AISystemResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/organizations/{org_slug}/ai-systems", response_model=AISystemResponse, status_code=201)
async def create_ai_system(
    org_slug: str,
    body: AISystemCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AISystemResponse:
    """Create a new AI system in the organisation registry."""
    org = await _get_org_by_slug(org_slug, db)

    repo = BaseRepository(AISystem, db)
    data = body.model_dump(exclude_none=False)
    # Rename metadata_ → metadata for the model
    if "metadata_" in data:
        data["metadata_"] = data.pop("metadata_") or {}
    data["organization_id"] = org.id
    data["owner_id"] = current_user.id

    system = await repo.create(data)

    await create_audit_event(
        db, AuditAction.AI_SYSTEM_CREATED,
        actor_id=current_user.id, actor_email=current_user.email,
        organization_id=org.id,
        resource_type="ai_system", resource_id=system.id,
        request=request,
        metadata={"name": system.name, "lifecycle_status": system.lifecycle_status.value},
    )

    return AISystemResponse.model_validate(system)


@router.get("/organizations/{org_slug}/ai-systems/{system_id}", response_model=AISystemResponse)
async def get_ai_system(
    org_slug: str,
    system_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AISystemResponse:
    """Retrieve a single AI system."""
    org = await _get_org_by_slug(org_slug, db)
    repo = BaseRepository(AISystem, db)
    system = await repo.get(system_id, org.id)
    return AISystemResponse.model_validate(system)


@router.patch("/organizations/{org_slug}/ai-systems/{system_id}", response_model=AISystemResponse)
async def update_ai_system(
    org_slug: str,
    system_id: UUID,
    body: AISystemUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AISystemResponse:
    """Update fields on an existing AI system."""
    org = await _get_org_by_slug(org_slug, db)
    repo = BaseRepository(AISystem, db)

    update_data = {k: v for k, v in body.model_dump(exclude_unset=True).items() if v is not None}

    system = await repo.update(system_id, org.id, update_data)

    await create_audit_event(
        db, AuditAction.AI_SYSTEM_UPDATED,
        actor_id=current_user.id, actor_email=current_user.email,
        organization_id=org.id,
        resource_type="ai_system", resource_id=system.id,
        request=request,
        metadata={"updated_fields": list(update_data.keys())},
    )

    return AISystemResponse.model_validate(system)


@router.delete("/organizations/{org_slug}/ai-systems/{system_id}", status_code=204)
async def delete_ai_system(
    org_slug: str,
    system_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete an AI system."""
    org = await _get_org_by_slug(org_slug, db)
    repo = BaseRepository(AISystem, db)
    await repo.soft_delete(system_id, org.id)

    await create_audit_event(
        db, AuditAction.AI_SYSTEM_DELETED,
        actor_id=current_user.id, actor_email=current_user.email,
        organization_id=org.id,
        resource_type="ai_system", resource_id=system_id,
        request=request,
    )
