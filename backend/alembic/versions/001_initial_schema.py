"""Initial schema — creates all Phase 0 tables.

Revision ID: 001
Revises: None
Create Date: 2026-10-13
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- Enum types ---------------------------------------------------------

    op.execute("""
        CREATE TYPE organization_status AS ENUM (
            'ACTIVE', 'SUSPENDED', 'TRIAL', 'PENDING'
        )
    """)
    op.execute("""
        CREATE TYPE risk_classification AS ENUM (
            'PROHIBITED', 'HIGH_RISK', 'LIMITED_TRANSPARENCY',
            'MINIMAL_OR_NO_RISK', 'NEEDS_REVIEW', 'UNCLASSIFIED'
        )
    """)
    op.execute("""
        CREATE TYPE ai_system_status AS ENUM (
            'DISCOVERED', 'DRAFT', 'IN_REVIEW', 'APPROVED',
            'ACTIVE', 'SUSPENDED', 'RETIRED'
        )
    """)
    op.execute("""
        CREATE TYPE deployment_environment AS ENUM (
            'PRODUCTION', 'STAGING', 'DEVELOPMENT', 'TESTING', 'RESEARCH'
        )
    """)

    # ---- organizations ------------------------------------------------------

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "ACTIVE", "SUSPENDED", "TRIAL", "PENDING",
                name="organization_status", create_type=False
            ),
            nullable=False,
            server_default="TRIAL",
        ),
        sa.Column("plan", sa.String(50), nullable=False, server_default="starter"),
        sa.Column("max_users", sa.Integer, nullable=False, server_default="10"),
        sa.Column("settings", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("logo_url", sa.String(2048), nullable=True),
        sa.Column("website", sa.String(2048), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
        sa.UniqueConstraint("name", name="uq_organizations_name"),
        sa.CheckConstraint("max_users > 0", name="ck_organizations_max_users_positive"),
    )
    op.create_index("ix_organizations_status", "organizations", ["status"])
    op.create_index("ix_organizations_created_at", "organizations", ["created_at"])

    # ---- users --------------------------------------------------------------

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_superuser", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("avatar_url", sa.String(2048), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_created_at", "users", ["created_at"])

    # ---- organization_members -----------------------------------------------

    op.create_table(
        "organization_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="READ_ONLY"),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("invited_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("joined_at", sa.Text, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["invited_by"], ["users.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint(
            "organization_id", "user_id", name="uq_org_members_org_user"
        ),
    )
    op.create_index(
        "ix_org_members_organization_id", "organization_members", ["organization_id"]
    )
    op.create_index("ix_org_members_user_id", "organization_members", ["user_id"])
    op.create_index("ix_org_members_role", "organization_members", ["role"])

    # ---- ai_systems ---------------------------------------------------------

    op.create_table(
        "ai_systems",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("business_purpose", sa.Text, nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("provider", sa.String(255), nullable=True),
        sa.Column("model_name", sa.String(255), nullable=True),
        sa.Column("model_version", sa.String(100), nullable=True),
        sa.Column(
            "deployment_environment",
            postgresql.ENUM(
                "PRODUCTION", "STAGING", "DEVELOPMENT", "TESTING", "RESEARCH",
                name="deployment_environment", create_type=False
            ),
            nullable=True,
        ),
        sa.Column("business_domain", sa.String(255), nullable=True),
        sa.Column("user_count_estimate", sa.Integer, nullable=True),
        sa.Column(
            "data_categories", postgresql.JSONB, nullable=False, server_default="[]"
        ),
        sa.Column(
            "risk_classification",
            postgresql.ENUM(
                "PROHIBITED", "HIGH_RISK", "LIMITED_TRANSPARENCY",
                "MINIMAL_OR_NO_RISK", "NEEDS_REVIEW", "UNCLASSIFIED",
                name="risk_classification", create_type=False
            ),
            nullable=False,
            server_default="UNCLASSIFIED",
        ),
        sa.Column(
            "lifecycle_status",
            postgresql.ENUM(
                "DISCOVERED", "DRAFT", "IN_REVIEW", "APPROVED",
                "ACTIVE", "SUSPENDED", "RETIRED",
                name="ai_system_status", create_type=False
            ),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("regulatory_status", sa.String(100), nullable=True),
        sa.Column("review_date", sa.Date, nullable=True),
        sa.Column(
            "metadata", postgresql.JSONB, nullable=False, server_default="{}"
        ),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint(
            "organization_id", "name", name="uq_ai_systems_org_name"
        ),
        sa.CheckConstraint(
            "user_count_estimate IS NULL OR user_count_estimate >= 0",
            name="ck_ai_systems_user_count_nonneg",
        ),
    )
    op.create_index("ix_ai_systems_organization_id", "ai_systems", ["organization_id"])
    op.create_index("ix_ai_systems_lifecycle_status", "ai_systems", ["lifecycle_status"])
    op.create_index(
        "ix_ai_systems_risk_classification", "ai_systems", ["risk_classification"]
    )
    op.create_index("ix_ai_systems_owner_id", "ai_systems", ["owner_id"])
    op.create_index("ix_ai_systems_created_at", "ai_systems", ["created_at"])

    # ---- audit_events -------------------------------------------------------

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_email", sa.String(320), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("correlation_id", sa.String(64), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column(
            "metadata", postgresql.JSONB, nullable=False, server_default="{}"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_audit_events_organization_id", "audit_events", ["organization_id"]
    )
    op.create_index("ix_audit_events_actor_id", "audit_events", ["actor_id"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])
    op.create_index(
        "ix_audit_events_resource_type_id",
        "audit_events",
        ["resource_type", "resource_id"],
    )
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])
    op.create_index(
        "ix_audit_events_correlation_id", "audit_events", ["correlation_id"]
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("ai_systems")
    op.drop_table("organization_members")
    op.drop_table("users")
    op.drop_table("organizations")

    op.execute("DROP TYPE IF EXISTS deployment_environment")
    op.execute("DROP TYPE IF EXISTS ai_system_status")
    op.execute("DROP TYPE IF EXISTS risk_classification")
    op.execute("DROP TYPE IF EXISTS organization_status")
