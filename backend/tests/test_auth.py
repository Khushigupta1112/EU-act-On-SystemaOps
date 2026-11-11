import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_flow(client: AsyncClient):
    payload = {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "organization_name": "Acme Corp",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["organization_slug"] == "acme-corp"

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, setup_tenants):
    payload = {
        "email": "admin@alpha.com",
        "password": "AlphaPass123!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@alpha.com"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, setup_tenants):
    payload = {
        "email": "admin@alpha.com",
        "password": "WrongPassword!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient, setup_tenants):
    token = setup_tenants["token_a"]
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@alpha.com"
