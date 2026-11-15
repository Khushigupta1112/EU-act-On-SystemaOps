import asyncio
import os
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-chars-long"

from app.database import Base, get_db
from app.main import app
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.models.role import UserRole
from app.models.ai_system import AISystem, RiskClassification, AISystemStatus
from app.core.security import get_password_hash, create_access_token

# In-memory SQLite async engine for lightning fast isolation tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(prepare_database) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def setup_tenants(db_session: AsyncSession):
    # Org A
    org_a = Organization(
        name="Org Alpha",
        slug="org-alpha",
        display_name="Organization Alpha",
    )
    # Org B
    org_b = Organization(
        name="Org Beta",
        slug="org-beta",
        display_name="Organization Beta",
    )
    db_session.add_all([org_a, org_b])
    await db_session.flush()

    # User in Org A (Admin)
    user_a = User(
        email="admin@alpha.com",
        hashed_password=get_password_hash("AlphaPass123!"),
        full_name="Alpha Admin",
        is_active=True,
        is_verified=True,
    )
    # User in Org B (Admin)
    user_b = User(
        email="admin@beta.com",
        hashed_password=get_password_hash("BetaPass123!"),
        full_name="Beta Admin",
        is_active=True,
        is_verified=True,
    )
    # User Read-Only in Org A
    user_readonly = User(
        email="viewer@alpha.com",
        hashed_password=get_password_hash("ViewerPass123!"),
        full_name="Alpha Viewer",
        is_active=True,
        is_verified=True,
    )
    db_session.add_all([user_a, user_b, user_readonly])
    await db_session.flush()

    member_a = OrganizationMember(
        organization_id=org_a.id,
        user_id=user_a.id,
        role=UserRole.ORG_ADMIN,
        is_primary=True,
    )
    member_b = OrganizationMember(
        organization_id=org_b.id,
        user_id=user_b.id,
        role=UserRole.ORG_ADMIN,
        is_primary=True,
    )
    member_readonly = OrganizationMember(
        organization_id=org_a.id,
        user_id=user_readonly.id,
        role=UserRole.READ_ONLY,
        is_primary=True,
    )
    db_session.add_all([member_a, member_b, member_readonly])

    # AI System in Org A
    ai_a = AISystem(
        organization_id=org_a.id,
        name="Alpha Customer Churn Predictor",
        risk_classification=RiskClassification.HIGH_RISK,
        lifecycle_status=AISystemStatus.ACTIVE,
    )
    # AI System in Org B
    ai_b = AISystem(
        organization_id=org_b.id,
        name="Beta Resume Screener",
        risk_classification=RiskClassification.HIGH_RISK,
        lifecycle_status=AISystemStatus.ACTIVE,
    )
    db_session.add_all([ai_a, ai_b])
    await db_session.commit()

    token_a = create_access_token(
        user_id=user_a.id,
        organization_id=org_a.id,
        role=UserRole.ORG_ADMIN.value,
    )
    token_b = create_access_token(
        user_id=user_b.id,
        organization_id=org_b.id,
        role=UserRole.ORG_ADMIN.value,
    )
    token_readonly = create_access_token(
        user_id=user_readonly.id,
        organization_id=org_a.id,
        role=UserRole.READ_ONLY.value,
    )

    return {
        "org_a": org_a,
        "org_b": org_b,
        "user_a": user_a,
        "user_b": user_b,
        "user_readonly": user_readonly,
        "ai_a": ai_a,
        "ai_b": ai_b,
        "token_a": token_a,
        "token_b": token_b,
        "token_readonly": token_readonly,
    }
