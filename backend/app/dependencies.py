"""
FastAPI dependency injection functions.

These are used with FastAPI's ``Depends()`` system to:
1. Extract and validate the current authenticated user from JWT tokens.
2. Resolve the user's role within a specific organisation.
3. Enforce permission checks at the endpoint level.
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Path, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AccountLockedError,
    PermissionDeniedError,
    TenantViolationError,
    TokenExpiredError,
    TokenInvalidError,
)
from app.core.security import decode_token
from app.database import get_db
from app.models.role import Permission, UserRole, has_permission
from app.models.user import User
from app.models.organization import Organization, OrganizationMember

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract, validate, and return the authenticated user from the Bearer token.

    Raises HTTPException 401 on any auth failure so that FastAPI's OpenAPI
    UI documents the 401 response correctly.
    """
    from sqlalchemy import select

    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except TokenInvalidError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled.")
    if user.is_locked:
        raise HTTPException(status_code=403, detail="Account is temporarily locked.")

    org_id_str = payload.get("org_id")
    role_str = payload.get("role")
    setattr(user, "token_payload", payload)
    try:
        setattr(user, "current_organization_id", UUID(org_id_str) if org_id_str else None)
    except ValueError:
        setattr(user, "current_organization_id", None)
    try:
        setattr(user, "current_role", UserRole(role_str) if role_str else None)
    except ValueError:
        setattr(user, "current_role", None)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Alias dependency — same as get_current_user but named for clarity."""
    return current_user


def get_org_member_dependency(require_role: UserRole | None = None):
    """
    Factory that returns a dependency resolving the current user's membership
    in the organization identified by ``{org_slug}`` path parameter.

    Parameters
    ----------
    require_role:
        If set, raises 403 if the member's role is below this level.
    """

    async def _resolve(
        org_slug: str = Path(..., description="Organisation URL slug"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> OrganizationMember:
        from sqlalchemy import select

        # Resolve organisation by slug
        org_result = await db.execute(
            select(Organization).where(
                Organization.slug == org_slug,
                Organization.deleted_at.is_(None),
            )
        )
        org: Organization | None = org_result.scalar_one_or_none()
        if org is None:
            raise HTTPException(status_code=404, detail="Organisation not found.")

        # Super-admins bypass membership checks
        if current_user.is_superuser:
            # Synthesize a virtual membership for super-admins
            virtual = OrganizationMember()
            virtual.organization_id = org.id
            virtual.user_id = current_user.id
            virtual.role = UserRole.SUPER_ADMIN.value
            return virtual

        # Resolve membership
        member_result = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org.id,
                OrganizationMember.user_id == current_user.id,
            )
        )
        member: OrganizationMember | None = member_result.scalar_one_or_none()
        if member is None:
            raise HTTPException(
                status_code=403, detail="You are not a member of this organisation."
            )

        return member

    return _resolve


def require_permission(permission: Permission):
    """
    Dependency factory that enforces a specific permission on the current member.
    Resolves organization scope from URL path parameter {org_slug} or from the authenticated
    user's token context and membership.

    Usage::

        @router.get("/sensitive")
        async def sensitive_endpoint(
            member: OrganizationMember = Depends(require_permission(Permission.AI_SYSTEM_CREATE)),
        ):
            ...
    """

    async def _check(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> OrganizationMember:
        from sqlalchemy import select

        org_slug = request.path_params.get("org_slug")
        org_id: UUID | None = None
        role: UserRole | None = None

        if current_user.is_superuser:
            role = UserRole.SUPER_ADMIN
            if org_slug:
                org_result = await db.execute(
                    select(Organization).where(
                        Organization.slug == org_slug,
                        Organization.deleted_at.is_(None),
                    )
                )
                org = org_result.scalar_one_or_none()
                if org is None:
                    raise HTTPException(status_code=404, detail="Organisation not found.")
                org_id = org.id
            else:
                org_id = getattr(current_user, "current_organization_id", None)
        else:
            if org_slug:
                org_result = await db.execute(
                    select(Organization).where(
                        Organization.slug == org_slug,
                        Organization.deleted_at.is_(None),
                    )
                )
                org = org_result.scalar_one_or_none()
                if org is None:
                    raise HTTPException(status_code=404, detail="Organisation not found.")
                org_id = org.id

                member_result = await db.execute(
                    select(OrganizationMember).where(
                        OrganizationMember.organization_id == org.id,
                        OrganizationMember.user_id == current_user.id,
                    )
                )
                member: OrganizationMember | None = member_result.scalar_one_or_none()
                if member is None:
                    raise HTTPException(
                        status_code=403, detail="You are not a member of this organisation."
                    )
                role = UserRole(member.role)
            else:
                org_id = getattr(current_user, "current_organization_id", None)
                role = getattr(current_user, "current_role", None)

                if not org_id:
                    member_result = await db.execute(
                        select(OrganizationMember).where(
                            OrganizationMember.user_id == current_user.id,
                            OrganizationMember.is_primary.is_(True),
                        )
                    )
                    member = member_result.scalar_one_or_none()
                    if member:
                        org_id = member.organization_id
                        role = UserRole(member.role)
                    else:
                        raise HTTPException(status_code=400, detail="No active organisation context.")
                elif not role:
                    member_result = await db.execute(
                        select(OrganizationMember).where(
                            OrganizationMember.organization_id == org_id,
                            OrganizationMember.user_id == current_user.id,
                        )
                    )
                    member = member_result.scalar_one_or_none()
                    if not member:
                        raise HTTPException(status_code=403, detail="You are not a member of this organisation.")
                    role = UserRole(member.role)

        if not has_permission(role, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission.value}' required.",
            )

        virtual = OrganizationMember()
        virtual.organization_id = org_id
        virtual.user_id = current_user.id
        virtual.role = role.value
        return virtual

    return _check
