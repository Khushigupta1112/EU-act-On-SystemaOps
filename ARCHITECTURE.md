# SystemaOps Technical Architecture Specification

## 1. System Topology & Layers

The SystemaOps platform is engineered as an enterprise-grade control-plane distributed across four decoupled layers:

1. **Presentation Layer (Web UI)**
   - Framework: Next.js 14 (App Router) + React 18 + TypeScript.
   - Styling & UI: Tailwind CSS + shadcn/ui components.
   - State & Data Fetching: TanStack Query (React Query) + Zustand.
   - Interceptors: Automated JWT refresh rotation & tenant routing.

2. **Application Control Plane (FastAPI REST Backend)**
   - API Framework: FastAPI (Python 3.11+ / 3.12).
   - Validation & Serialization: Pydantic v2 schemas.
   - Database Access: Async SQLAlchemy 2.0 with PostgreSQL (`asyncpg`).
   - Tenant Boundary: `organization_id` isolation enforced across repository patterns and JWT scopes.
   - RBAC Engine: 11 distinct personas mapped to granular resource permissions.

3. **Persistence & Audit Subsystem**
   - RDBMS: PostgreSQL 16 (with connection pooling via async SQLAlchemy).
   - Migrations: Alembic async version tracking.
   - Audit Trail: Immutable append-only `audit_events` schema capturing actor, org, resource, IP, user-agent, and before/after metadata.

4. **Integration & Adapter Mesh**
   - Open-source adapters for OSCAL, EU AI Act toolkits, and LLM blackbox evaluation pipelines.

---

## 2. Multi-Tenancy Architecture

Multi-tenancy is enforced natively:
- Every tenant model inherits `BaseModel` and has an explicit `organization_id` foreign key.
- Repositories (`BaseRepository[ModelType]`) require `organization_id` for all queries and raise `TenantViolationError` (HTTP 403) on any cross-tenant leakage.
- JWT tokens include `org_id` claims, ensuring users can only interact with resources within their authorized organization.

---

## 3. RBAC Persona Hierarchy
The platform implements 11 standard roles:
- `SUPER_ADMIN`: Platform operations & maintenance.
- `ORG_ADMIN`: Organization owner and administrative controller.
- `AI_GOVERNANCE`: Compliance architect with oversight across all inventory and controls.
- `COMPLIANCE_MANAGER`: Manages assessments, gap analyses, and compliance reporting.
- `PRIVACY_OFFICER`: Supervises GDPR, data categories, and consent reviews.
- `SECURITY_MANAGER`: Controls incident responses and security testing.
- `AI_SYSTEM_OWNER`: Registers and maintains metadata for assigned AI workloads.
- `REVIEWER`: Conducts peer assessments and review approvals.
- `AUDITOR`: Read-only access with complete audit ledger verification privileges.
- `EMPLOYEE`: Access to AI literacy training and policy checklists.
- `READ_ONLY`: Observer persona without mutation capabilities.
