"""
Role and permission definitions for SystemaOps RBAC.

UserRole and Permission are plain Python enums (not database-stored enums)
so that they can be referenced in Python code without a database round-trip.
ROLE_PERMISSIONS maps each role to the set of permissions it holds.
"""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """All user roles in the system, ordered from highest to lowest privilege."""

    SUPER_ADMIN = "SUPER_ADMIN"
    """Platform super-administrator. Has unrestricted access across all tenants."""

    ORG_ADMIN = "ORG_ADMIN"
    """Organisation administrator. Full control within a single tenant."""

    AI_GOVERNANCE = "AI_GOVERNANCE"
    """AI Governance lead. Manages all AI systems, assessments, and policies."""

    COMPLIANCE_MANAGER = "COMPLIANCE_MANAGER"
    """Compliance Manager. Oversees compliance frameworks, evidence, and reports."""

    PRIVACY_OFFICER = "PRIVACY_OFFICER"
    """Privacy Officer / DPO. Manages data privacy and DPIA-related tasks."""

    SECURITY_MANAGER = "SECURITY_MANAGER"
    """Security Manager. Manages security controls and risk reviews."""

    AI_SYSTEM_OWNER = "AI_SYSTEM_OWNER"
    """Business owner of one or more AI systems. Can manage their own systems."""

    REVIEWER = "REVIEWER"
    """Cross-functional reviewer. Can comment and approve/reject assessments."""

    AUDITOR = "AUDITOR"
    """Internal or external auditor. Read-only except for audit evidence collection."""

    EMPLOYEE = "EMPLOYEE"
    """Standard employee. Can submit AI use disclosures and view policies."""

    READ_ONLY = "READ_ONLY"
    """Read-only observer. No write access whatsoever."""


class Permission(str, Enum):
    """Granular permission tokens used for RBAC enforcement at the service layer."""

    # ---- Organisation management ----
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE_MEMBERS = "org:manage_members"
    ORG_MANAGE_BILLING = "org:manage_billing"
    ORG_VIEW_AUDIT_LOG = "org:view_audit_log"

    # ---- User management ----
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_INVITE = "user:invite"
    USER_MANAGE_ROLES = "user:manage_roles"

    # ---- AI System management ----
    AI_SYSTEM_READ = "ai_system:read"
    AI_SYSTEM_CREATE = "ai_system:create"
    AI_SYSTEM_UPDATE = "ai_system:update"
    AI_SYSTEM_DELETE = "ai_system:delete"
    AI_SYSTEM_CHANGE_STATUS = "ai_system:change_status"
    AI_SYSTEM_RECLASSIFY_RISK = "ai_system:reclassify_risk"
    AI_SYSTEM_EXPORT = "ai_system:export"

    # ---- Risk assessment ----
    ASSESSMENT_READ = "assessment:read"
    ASSESSMENT_CREATE = "assessment:create"
    ASSESSMENT_UPDATE = "assessment:update"
    ASSESSMENT_DELETE = "assessment:delete"
    ASSESSMENT_APPROVE = "assessment:approve"
    ASSESSMENT_REJECT = "assessment:reject"
    ASSESSMENT_SUBMIT = "assessment:submit"

    # ---- Compliance ----
    COMPLIANCE_READ = "compliance:read"
    COMPLIANCE_MANAGE = "compliance:manage"
    COMPLIANCE_EXPORT = "compliance:export"

    # ---- Evidence ----
    EVIDENCE_READ = "evidence:read"
    EVIDENCE_UPLOAD = "evidence:upload"
    EVIDENCE_DELETE = "evidence:delete"

    # ---- Policy ----
    POLICY_READ = "policy:read"
    POLICY_CREATE = "policy:create"
    POLICY_UPDATE = "policy:update"
    POLICY_DELETE = "policy:delete"
    POLICY_PUBLISH = "policy:publish"

    # ---- Reports ----
    REPORT_READ = "report:read"
    REPORT_CREATE = "report:create"
    REPORT_EXPORT = "report:export"

    # ---- Platform administration (SUPER_ADMIN only) ----
    PLATFORM_ADMIN = "platform:admin"
    PLATFORM_VIEW_ALL_ORGS = "platform:view_all_orgs"
    PLATFORM_MANAGE_ORGS = "platform:manage_orgs"


# ---------------------------------------------------------------------------
# Role → Permission mapping
# ---------------------------------------------------------------------------
# Each role accumulates the permissions of every less-privileged role it
# supersedes, plus its own unique permissions. This flat mapping is intentional
# (no runtime inheritance lookup) for audit clarity and predictability.
# ---------------------------------------------------------------------------

_BASE_READ: frozenset[Permission] = frozenset(
    {
        Permission.ORG_READ,
        Permission.USER_READ,
        Permission.AI_SYSTEM_READ,
        Permission.ASSESSMENT_READ,
        Permission.COMPLIANCE_READ,
        Permission.EVIDENCE_READ,
        Permission.POLICY_READ,
        Permission.REPORT_READ,
    }
)

ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.READ_ONLY: _BASE_READ,
    UserRole.EMPLOYEE: _BASE_READ
    | frozenset(
        {
            Permission.ASSESSMENT_SUBMIT,
        }
    ),
    UserRole.AUDITOR: _BASE_READ
    | frozenset(
        {
            Permission.EVIDENCE_UPLOAD,
            Permission.REPORT_CREATE,
            Permission.COMPLIANCE_EXPORT,
            Permission.REPORT_EXPORT,
            Permission.AI_SYSTEM_EXPORT,
            Permission.ORG_VIEW_AUDIT_LOG,
        }
    ),
    UserRole.REVIEWER: _BASE_READ
    | frozenset(
        {
            Permission.ASSESSMENT_APPROVE,
            Permission.ASSESSMENT_REJECT,
            Permission.EVIDENCE_UPLOAD,
        }
    ),
    UserRole.AI_SYSTEM_OWNER: _BASE_READ
    | frozenset(
        {
            Permission.AI_SYSTEM_CREATE,
            Permission.AI_SYSTEM_UPDATE,
            Permission.AI_SYSTEM_CHANGE_STATUS,
            Permission.AI_SYSTEM_EXPORT,
            Permission.ASSESSMENT_CREATE,
            Permission.ASSESSMENT_UPDATE,
            Permission.ASSESSMENT_SUBMIT,
            Permission.EVIDENCE_UPLOAD,
        }
    ),
    UserRole.SECURITY_MANAGER: _BASE_READ
    | frozenset(
        {
            Permission.AI_SYSTEM_CREATE,
            Permission.AI_SYSTEM_UPDATE,
            Permission.AI_SYSTEM_CHANGE_STATUS,
            Permission.AI_SYSTEM_RECLASSIFY_RISK,
            Permission.AI_SYSTEM_EXPORT,
            Permission.ASSESSMENT_CREATE,
            Permission.ASSESSMENT_UPDATE,
            Permission.ASSESSMENT_APPROVE,
            Permission.ASSESSMENT_REJECT,
            Permission.ASSESSMENT_SUBMIT,
            Permission.EVIDENCE_UPLOAD,
            Permission.EVIDENCE_DELETE,
            Permission.COMPLIANCE_MANAGE,
            Permission.COMPLIANCE_EXPORT,
            Permission.REPORT_CREATE,
            Permission.REPORT_EXPORT,
            Permission.ORG_VIEW_AUDIT_LOG,
        }
    ),
    UserRole.PRIVACY_OFFICER: _BASE_READ
    | frozenset(
        {
            Permission.AI_SYSTEM_UPDATE,
            Permission.AI_SYSTEM_EXPORT,
            Permission.ASSESSMENT_CREATE,
            Permission.ASSESSMENT_UPDATE,
            Permission.ASSESSMENT_SUBMIT,
            Permission.EVIDENCE_UPLOAD,
            Permission.EVIDENCE_DELETE,
            Permission.COMPLIANCE_MANAGE,
            Permission.COMPLIANCE_EXPORT,
            Permission.POLICY_CREATE,
            Permission.POLICY_UPDATE,
            Permission.POLICY_DELETE,
            Permission.POLICY_PUBLISH,
            Permission.REPORT_CREATE,
            Permission.REPORT_EXPORT,
            Permission.ORG_VIEW_AUDIT_LOG,
        }
    ),
    UserRole.COMPLIANCE_MANAGER: _BASE_READ
    | frozenset(
        {
            Permission.AI_SYSTEM_UPDATE,
            Permission.AI_SYSTEM_EXPORT,
            Permission.ASSESSMENT_CREATE,
            Permission.ASSESSMENT_UPDATE,
            Permission.ASSESSMENT_APPROVE,
            Permission.ASSESSMENT_REJECT,
            Permission.ASSESSMENT_SUBMIT,
            Permission.EVIDENCE_UPLOAD,
            Permission.EVIDENCE_DELETE,
            Permission.COMPLIANCE_MANAGE,
            Permission.COMPLIANCE_EXPORT,
            Permission.POLICY_CREATE,
            Permission.POLICY_UPDATE,
            Permission.POLICY_DELETE,
            Permission.POLICY_PUBLISH,
            Permission.REPORT_CREATE,
            Permission.REPORT_EXPORT,
            Permission.ORG_VIEW_AUDIT_LOG,
        }
    ),
    UserRole.AI_GOVERNANCE: frozenset(Permission)
    - frozenset(
        {
            Permission.PLATFORM_ADMIN,
            Permission.PLATFORM_VIEW_ALL_ORGS,
            Permission.PLATFORM_MANAGE_ORGS,
            Permission.ORG_MANAGE_BILLING,
            Permission.ORG_DELETE,
            Permission.USER_DELETE,
        }
    ),
    UserRole.ORG_ADMIN: frozenset(Permission)
    - frozenset(
        {
            Permission.PLATFORM_ADMIN,
            Permission.PLATFORM_VIEW_ALL_ORGS,
            Permission.PLATFORM_MANAGE_ORGS,
        }
    ),
    UserRole.SUPER_ADMIN: frozenset(Permission),
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Return True if *role* grants *permission*."""
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def get_permissions(role: UserRole) -> frozenset[Permission]:
    """Return the complete permission set for *role*."""
    return ROLE_PERMISSIONS.get(role, frozenset())
