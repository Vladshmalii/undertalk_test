
import pytest
from httpx import AsyncClient

from app.models.order_model import Order
from app.models.tenant_model import Tenant


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, test_tenant: Tenant) -> None:
    response = await client.post(
        f"/api/v1/tenants/{test_tenant.id}/orders",
        json={
            "title": "MacBook Pro M3",
            "amount": 2500.00,
            "status": "new",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "MacBook Pro M3"
    assert float(data["amount"]) == 2500.0
    assert data["status"] == "new"
    assert data["tenant_id"] == str(test_tenant.id)


@pytest.mark.asyncio
async def test_list_all_orders_with_meta(client: AsyncClient, test_order: Order) -> None:
    response = await client.get("/api/v1/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert data["meta"]["total"] >= 1
    assert data["meta"]["page"] == 1


@pytest.mark.asyncio
async def test_list_tenant_orders(client: AsyncClient, test_tenant: Tenant, test_order: Order) -> None:
    response = await client.get(f"/api/v1/tenants/{test_tenant.id}/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert data["items"][0]["tenant_id"] == str(test_tenant.id)


@pytest.mark.asyncio
async def test_update_order_status(client: AsyncClient, test_order: Order) -> None:
    response = await client.patch(
        f"/api/v1/orders/{test_order.id}/status",
        json={"status": "paid"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "paid"


@pytest.mark.asyncio
async def test_get_dashboard_stats(client: AsyncClient, test_order: Order) -> None:
    # Set to paid to test revenue
    await client.patch(f"/api/v1/orders/{test_order.id}/status", json={"status": "paid"})

    response = await client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] >= 1
    assert float(data["total_revenue"]) >= 99.99
    assert data["total_tenants"] >= 1
    assert "paid" in data["orders_by_status"]
