import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_cannot_read_other_org_ai_system(client: AsyncClient, setup_tenants):
    token_a = setup_tenants["token_a"]
    ai_b_id = setup_tenants["ai_b"].id
    headers = {"Authorization": f"Bearer {token_a}"}

    # User from Org A attempts to fetch AI System from Org B
    response = await client.get(f"/api/v1/ai-systems/{ai_b_id}", headers=headers)
    assert response.status_code in [403, 404]

@pytest.mark.asyncio
async def test_user_cannot_list_other_org_resources(client: AsyncClient, setup_tenants):
    token_a = setup_tenants["token_a"]
    headers = {"Authorization": f"Bearer {token_a}"}

    response = await client.get("/api/v1/ai-systems", headers=headers)
    assert response.status_code == 200
    data = response.json()
    items = data["items"]
    # Should only return Alpha's AI systems
    for item in items:
        assert item["organization_id"] == str(setup_tenants["org_a"].id)
        assert item["name"] == "Alpha Customer Churn Predictor"

@pytest.mark.asyncio
async def test_user_cannot_modify_other_org_ai_system(client: AsyncClient, setup_tenants):
    token_a = setup_tenants["token_a"]
    ai_b_id = setup_tenants["ai_b"].id
    headers = {"Authorization": f"Bearer {token_a}"}

    payload = {"name": "Hacked Beta System"}
    response = await client.patch(f"/api/v1/ai-systems/{ai_b_id}", json=payload, headers=headers)
    assert response.status_code in [403, 404]

@pytest.mark.asyncio
async def test_user_cannot_delete_other_org_ai_system(client: AsyncClient, setup_tenants):
    token_a = setup_tenants["token_a"]
    ai_b_id = setup_tenants["ai_b"].id
    headers = {"Authorization": f"Bearer {token_a}"}

    response = await client.delete(f"/api/v1/ai-systems/{ai_b_id}", headers=headers)
    assert response.status_code in [403, 404]

@pytest.mark.asyncio
async def test_user_cannot_access_foreign_org_slug_route(client: AsyncClient, setup_tenants):
    token_a = setup_tenants["token_a"]
    org_b_slug = setup_tenants["org_b"].slug
    headers = {"Authorization": f"Bearer {token_a}"}

    # Org A user attempts to list resources through Org B's URL slug
    response = await client.get(f"/api/v1/organizations/{org_b_slug}/ai-systems", headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_org_scoped_routes_work_for_valid_member(client: AsyncClient, setup_tenants):
    token_a = setup_tenants["token_a"]
    org_a_slug = setup_tenants["org_a"].slug
    headers = {"Authorization": f"Bearer {token_a}"}

    payload = {
        "name": "Scoped Route AI System",
        "risk_classification": "MINIMAL_OR_NO_RISK",
        "lifecycle_status": "DRAFT",
    }
    response = await client.post(
        f"/api/v1/organizations/{org_a_slug}/ai-systems", json=payload, headers=headers
    )
    assert response.status_code == 201
    created_id = response.json()["id"]

    get_resp = await client.get(
        f"/api/v1/organizations/{org_a_slug}/ai-systems/{created_id}", headers=headers
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Scoped Route AI System"
