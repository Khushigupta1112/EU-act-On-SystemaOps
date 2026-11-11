"""
Organization model — the tenant boundary for all SystemaOps data.

Every enterprise customer is represented as an Organization. All other
domain models carry an ``organization_id`` foreign key that enforces
tenant isolation at the database level.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum as SaEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class OrganizationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    PENDING = "PENDING"


class Organization(BaseModel):
    """
    Tenant entity. One row per enterprise customer.

    Constraints
    -----------
    - ``name`` and ``slug`` must be unique across all tenants.
    - ``slug`` is URL-safe and used in routing (e.g. /org/acme/...).
    - ``max_users`` is a soft limit enforced at the service layer.
    """

    __tablename__ = "organizations"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_organizations_slug"),
        UniqueConstraint("name", name="uq_organizations_name"),
        CheckConstraint("max_users > 0", name="ck_organizations_max_users_positive"),
        Index("ix_organizations_status", "status"),
        Index("ix_organizations_created_at", "created_at"),
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Human-readable organisation name."
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="URL-safe unique identifier used in routing.",
    )
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Short display name shown in the UI.",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[OrganizationStatus] = mapped_column(
        SaEnum(OrganizationStatus, name="organization_status"),
        nullable=False,
        default=OrganizationStatus.TRIAL,
        index=True,
    )
    plan: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="starter",
        comment="Subscription plan: starter | professional | enterprise.",
    )
    max_users: Mapped[int] = mapped_column(
        Integer, nullable=False, default=10
    )
    settings: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Tenant-specific feature flags and configuration.",
    )
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    website: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True, comment="ISO-3166-1 alpha-2")

    # ---- Relationships -------------------------------------------------------
    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organization id={self.id} slug={self.slug!r}>"


class OrganizationMember(BaseModel):
    """
    Association between a User and an Organization with a role assignment.

    A user can belong to multiple organizations (e.g. a consultant), but
    one is marked as ``is_primary``.
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_org_members_org_user",
        ),
        Index("ix_org_members_organization_id", "organization_id"),
        Index("ix_org_members_user_id", "user_id"),
        Index("ix_org_members_role", "role"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="READ_ONLY",
        comment="UserRole enum value.",
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if this is the user's default organisation.",
    )
    invited_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    joined_at: Mapped[str | None] = mapped_column(nullable=True)

    # ---- Relationships -------------------------------------------------------
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="members", lazy="select"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<OrganizationMember org={self.organization_id} "
            f"user={self.user_id} role={self.role!r}>"
        )
