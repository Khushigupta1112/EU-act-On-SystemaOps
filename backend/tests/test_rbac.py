import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_only_cannot_create_ai_system(client: AsyncClient, setup_tenants):
    token_ro = setup_tenants["token_readonly"]
    headers = {"Authorization": f"Bearer {token_ro}"}

    payload = {
        "name": "Unauthorized AI Tool",
        "risk_classification": "MINIMAL_OR_NO_RISK",
        "lifecycle_status": "DRAFT",
    }
    response = await client.post("/api/v1/ai-systems", json=payload, headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_can_create_ai_system(client: AsyncClient, setup_tenants):
    token_a = setup_tenants["token_a"]
    headers = {"Authorization": f"Bearer {token_a}"}

    payload = {
        "name": "Approved AI Tool",
        "risk_classification": "MINIMAL_OR_NO_RISK",
        "lifecycle_status": "DRAFT",
    }
    response = await client.post("/api/v1/ai-systems", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Approved AI Tool"

@pytest.mark.asyncio
async def test_read_only_cannot_delete_ai_system(client: AsyncClient, setup_tenants):
    token_ro = setup_tenants["token_readonly"]
    ai_a_id = setup_tenants["ai_a"].id
    headers = {"Authorization": f"Bearer {token_ro}"}

    response = await client.delete(f"/api/v1/ai-systems/{ai_a_id}", headers=headers)
    assert response.status_code == 403
