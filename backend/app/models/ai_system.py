"""
AI System model — the central registry entity.

Each AI System represents a deployed or planned AI solution owned by a
tenant organization. This is the anchor entity for risk classification,
evidence, controls, assessments, incidents, and vendor relationships.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
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


class RiskClassification(str, enum.Enum):
    PROHIBITED = "PROHIBITED"
    HIGH_RISK = "HIGH_RISK"
    LIMITED_TRANSPARENCY = "LIMITED_TRANSPARENCY"
    MINIMAL_OR_NO_RISK = "MINIMAL_OR_NO_RISK"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    UNCLASSIFIED = "UNCLASSIFIED"


class AISystemStatus(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class DeploymentEnvironment(str, enum.Enum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    RESEARCH = "RESEARCH"


class AISystem(BaseModel):
    """
    Central AI System registry record.

    Tenant isolation
    ----------------
    ``organization_id`` is the tenant boundary. Every query against this
    table MUST filter by ``organization_id``. The repository layer enforces
    this; never bypass it with raw SQL in request handlers.

    Risk classification
    -------------------
    ``risk_classification`` is set by the risk-classification engine or by
    a qualified human reviewer. It must never be silently set to PASS by
    an automated process without human confirmation for HIGH_RISK+ systems.
    """

    __tablename__ = "ai_systems"
    __table_args__ = (
        Index("ix_ai_systems_organization_id", "organization_id"),
        Index("ix_ai_systems_lifecycle_status", "lifecycle_status"),
        Index("ix_ai_systems_risk_classification", "risk_classification"),
        Index("ix_ai_systems_owner_id", "owner_id"),
        Index("ix_ai_systems_created_at", "created_at"),
        UniqueConstraint(
            "organization_id", "name",
            name="uq_ai_systems_org_name",
        ),
        CheckConstraint(
            "user_count_estimate IS NULL OR user_count_estimate >= 0",
            name="ck_ai_systems_user_count_nonneg",
        ),
    )

    # ---- Tenant boundary -----------------------------------------------------
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant boundary — MUST be filtered on every query.",
    )

    # ---- Core identity -------------------------------------------------------
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- Ownership -----------------------------------------------------------
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Technical details ---------------------------------------------------
    provider: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Vendor / provider name."
    )
    model_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deployment_environment: Mapped[DeploymentEnvironment | None] = mapped_column(
        SaEnum(DeploymentEnvironment, name="deployment_environment"),
        nullable=True,
    )
    business_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Impact scope --------------------------------------------------------
    user_count_estimate: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Approximate number of affected end-users."
    )
    data_categories: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="List of data category labels (e.g. ['personal', 'biometric']).",
    )

    # ---- Classification & status ---------------------------------------------
    risk_classification: Mapped[RiskClassification] = mapped_column(
        SaEnum(RiskClassification, name="risk_classification"),
        nullable=False,
        default=RiskClassification.UNCLASSIFIED,
        index=True,
    )
    lifecycle_status: Mapped[AISystemStatus] = mapped_column(
        SaEnum(AISystemStatus, name="ai_system_status"),
        nullable=False,
        default=AISystemStatus.DRAFT,
        index=True,
    )
    regulatory_status: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ---- Review schedule -----------------------------------------------------
    review_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ---- Metadata ------------------------------------------------------------
    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        comment="Flexible key-value store for additional attributes.",
    )

    # ---- Relationships -------------------------------------------------------
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        "Organization", lazy="select"
    )
    owner: Mapped["User | None"] = relationship(  # noqa: F821
        "User", foreign_keys=[owner_id], lazy="select"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AISystem id={self.id} name={self.name!r} org={self.organization_id}>"
