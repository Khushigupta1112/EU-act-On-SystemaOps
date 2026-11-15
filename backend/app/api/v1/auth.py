"""
Authentication API endpoints.

POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
GET  /api/v1/auth/me
PATCH /api/v1/auth/me
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.audit import AuditAction, create_audit_event
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_email_verification_token,
    generate_password_reset_token,
    hash_password,
    needs_rehash,
    verify_password,
    verify_password_reset_token,
)
from app.core.exceptions import TokenExpiredError, TokenInvalidError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.organization import Organization, OrganizationMember
from app.models.role import UserRole
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


def _slugify(name: str) -> str:
    """Convert an organisation name to a URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:100]


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Register a new user and create their first Organisation.

    Creates:
    1. User record
    2. Organization record
    3. OrganizationMember linking them as ORG_ADMIN
    4. Audit events for registration and org creation
    """
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    # Build slug and ensure uniqueness
    base_slug = _slugify(body.organization_name)
    slug = base_slug
    counter = 1
    while True:
        existing_org = await db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        if existing_org.scalar_one_or_none() is None:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create user
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        is_active=True,
        is_verified=False,  # require email verification
        is_superuser=False,
        password_changed_at=datetime.now(UTC),
    )
    db.add(user)
    await db.flush()

    # Create organization
    org = Organization(
        name=body.organization_name,
        slug=slug,
        display_name=body.organization_name,
        plan="starter",
        max_users=10,
        settings={},
    )
    db.add(org)
    await db.flush()

    # Create membership
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=UserRole.ORG_ADMIN.value,
        is_primary=True,
        joined_at=datetime.now(UTC).isoformat(),
    )
    db.add(member)
    await db.flush()

    # Audit events
    await create_audit_event(
        db,
        action=AuditAction.USER_REGISTERED,
        actor_id=user.id,
        actor_email=user.email,
        organization_id=org.id,
        resource_type="user",
        resource_id=user.id,
        request=request,
        metadata={"email": user.email, "organization_name": org.name},
    )
    await create_audit_event(
        db,
        action=AuditAction.ORGANIZATION_CREATED,
        actor_id=user.id,
        actor_email=user.email,
        organization_id=org.id,
        resource_type="organization",
        resource_id=org.id,
        request=request,
        metadata={"name": org.name, "slug": org.slug},
    )

    # Issue tokens
    access_token = create_access_token(
        user_id=user.id, organization_id=org.id, role=UserRole.ORG_ADMIN.value
    )
    refresh_token = create_refresh_token(
        user_id=user.id, organization_id=org.id, role=UserRole.ORG_ADMIN.value
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "organization_slug": org.slug,
        },
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email/password and receive JWT tokens."""
    result = await db.execute(
        select(User).where(User.email == body.email, User.deleted_at.is_(None))
    )
    user: User | None = result.scalar_one_or_none()

    # Generic failure message to prevent user enumeration
    _invalid = HTTPException(status_code=401, detail="Invalid email or password.")

    if user is None:
        await create_audit_event(
            db, AuditAction.USER_LOGIN_FAILED,
            metadata={"email": body.email, "reason": "user_not_found"},
            request=request,
        )
        raise _invalid

    if user.is_locked:
        raise HTTPException(
            status_code=403,
            detail=f"Account is locked. Try again later.",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")

    if not verify_password(body.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = datetime.now(UTC) + timedelta(
                minutes=settings.ACCOUNT_LOCKOUT_MINUTES
            )
            await create_audit_event(
                db, AuditAction.USER_ACCOUNT_LOCKED,
                actor_email=user.email,
                resource_type="user", resource_id=user.id,
                metadata={"locked_until": str(user.locked_until)},
                request=request,
            )
        await create_audit_event(
            db, AuditAction.USER_LOGIN_FAILED, actor_email=user.email,
            resource_type="user", resource_id=user.id,
            metadata={"attempts": user.failed_login_attempts},
            request=request,
        )
        raise _invalid

    # Successful login — reset lockout counters
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.now(UTC)

    # Upgrade hash if needed
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(body.password)

    # Resolve primary organisation for token
    member_result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.is_primary.is_(True),
        )
    )
    member: OrganizationMember | None = member_result.scalar_one_or_none()
    org_id = member.organization_id if member else None
    role = member.role if member else UserRole.READ_ONLY.value

    org_slug = None
    if org_id:
        org_result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org_obj = org_result.scalar_one_or_none()
        if org_obj:
            org_slug = org_obj.slug

    await create_audit_event(
        db, AuditAction.USER_LOGIN,
        actor_id=user.id, actor_email=user.email,
        organization_id=org_id,
        resource_type="user", resource_id=user.id,
        request=request,
    )

    access_token = create_access_token(
        user_id=user.id, organization_id=org_id, role=role
    )
    refresh_token = create_refresh_token(
        user_id=user.id, organization_id=org_id, role=role
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "organization_slug": org_slug,
        },
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Exchange a refresh token for a new access + refresh token pair."""
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
    except (TokenExpiredError, TokenInvalidError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    user_id = uuid.UUID(payload["sub"])
    org_id_str = payload.get("org_id")
    org_id = uuid.UUID(org_id_str) if org_id_str else None
    role = payload.get("role", UserRole.READ_ONLY.value)

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None), User.is_active.is_(True))
    )
    user: User | None = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    new_access = create_access_token(user_id=user.id, organization_id=org_id, role=role)
    new_refresh = create_refresh_token(user_id=user.id, organization_id=org_id, role=role)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Log out the current user (audit event only; stateless JWT)."""
    await create_audit_event(
        db, AuditAction.USER_LOGOUT,
        actor_id=current_user.id, actor_email=current_user.email,
        resource_type="user", resource_id=current_user.id,
        request=request,
    )
    return MessageResponse(message="Logged out successfully.")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Request a password-reset email.

    Always returns success to prevent email enumeration. In production,
    wire to an SMTP service or a transactional email provider.
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user: User | None = result.scalar_one_or_none()

    if user is not None:
        _token = generate_password_reset_token(user.email)
        # TODO: send _token via email service
        await create_audit_event(
            db, AuditAction.USER_PASSWORD_RESET_REQUESTED,
            actor_email=user.email,
            resource_type="user", resource_id=user.id,
            request=request,
        )

    return MessageResponse(
        message="If that email is registered, a reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Complete a password reset using the token from the reset email."""
    try:
        from app.core.security import verify_password_reset_token
        email = verify_password_reset_token(body.token)
    except (TokenExpiredError, TokenInvalidError):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    result = await db.execute(select(User).where(User.email == email))
    user: User | None = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid reset token.")

    user.hashed_password = hash_password(body.new_password)
    user.password_changed_at = datetime.now(UTC)
    user.failed_login_attempts = 0
    user.locked_until = None

    await create_audit_event(
        db, AuditAction.USER_PASSWORD_RESET_COMPLETED,
        actor_email=user.email,
        resource_type="user", resource_id=user.id,
        request=request,
    )

    return MessageResponse(message="Password has been reset successfully.")


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    """Return the authenticated user's profile and organisation memberships."""
    memberships_result = await db.execute(
        select(OrganizationMember, Organization)
        .join(Organization, Organization.id == OrganizationMember.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    memberships = [
        {
            "organization_id": str(member.organization_id),
            "organization_name": org.name,
            "organization_slug": org.slug,
            "role": member.role,
            "is_primary": member.is_primary,
        }
        for member, org in memberships_result.all()
    ]

    user_resp = UserResponse.model_validate(current_user)
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        avatar_url=current_user.avatar_url,
        timezone=current_user.timezone,
        locale=current_user.locale,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        user=user_resp,
        memberships=memberships,
    )


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update the authenticated user's profile fields."""
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.timezone is not None:
        current_user.timezone = body.timezone
    if body.locale is not None:
        current_user.locale = body.locale

    await db.flush()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)
