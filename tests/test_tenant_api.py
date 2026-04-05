
import pytest
from httpx import AsyncClient

from app.models.tenant_model import Tenant


@pytest.mark.asyncio
async def test_create_tenant(client: AsyncClient) -> None:
    response = await client.post("/api/v1/tenants", json={"name": "New Company LLC"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Company LLC"
    assert "id" in data
    assert data["orders_count"] == 0


@pytest.mark.asyncio
async def test_create_tenant_duplicate(client: AsyncClient, test_tenant: Tenant) -> None:
    response = await client.post("/api/v1/tenants", json={"name": test_tenant.name})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_tenants(client: AsyncClient, test_tenant: Tenant) -> None:
    response = await client.get("/api/v1/tenants")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert data["meta"]["total"] >= 1
    assert data["meta"]["page"] == 1


@pytest.mark.asyncio
async def test_get_tenant(client: AsyncClient, test_tenant: Tenant) -> None:
    response = await client.get(f"/api/v1/tenants/{test_tenant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_tenant.id)
    assert data["name"] == test_tenant.name


@pytest.mark.asyncio
async def test_update_tenant(client: AsyncClient, test_tenant: Tenant) -> None:
    response = await client.patch(f"/api/v1/tenants/{test_tenant.id}", json={"name": "Updated Name LLC"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name LLC"


@pytest.mark.asyncio
async def test_delete_tenant(client: AsyncClient, test_tenant: Tenant) -> None:
    response = await client.delete(f"/api/v1/tenants/{test_tenant.id}")
    assert response.status_code == 204

    check = await client.get(f"/api/v1/tenants/{test_tenant.id}")
    assert check.status_code == 404
