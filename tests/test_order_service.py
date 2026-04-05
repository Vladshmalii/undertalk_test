from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order_model import Order, OrderStatus
from app.models.tenant_model import Tenant
from app.repositories.order_repository import OrderRepository
from app.repositories.tenant_repository import TenantRepository
from app.schemas.order_schema import OrderCreate, OrderStatusUpdate
from app.services.order_service import OrderService


@pytest_asyncio.fixture
async def order_service(db_session: AsyncSession) -> OrderService:
    order_repo = OrderRepository(db_session)
    tenant_repo = TenantRepository(db_session)
    return OrderService(order_repo, tenant_repo)


@pytest.mark.asyncio
async def test_create_order_service(order_service: OrderService, test_tenant: Tenant) -> None:
    data = OrderCreate(
        title="Laptop Order",
        amount=Decimal("1500.00"),
        status=OrderStatus.NEW,
    )
    order = await order_service.create_order(test_tenant.id, data)
    assert order.title == "Laptop Order"
    assert order.amount == Decimal("1500.00")
    assert order.tenant_id == test_tenant.id


@pytest.mark.asyncio
async def test_update_order_status_service(order_service: OrderService, test_order: Order) -> None:
    data = OrderStatusUpdate(status=OrderStatus.PAID)
    order = await order_service.update_order_status(test_order.id, data)
    assert order.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_list_orders_filtering_service(order_service: OrderService, test_order: Order) -> None:
    orders, total = await order_service.list_orders(search="Test Order", status_filter=OrderStatus.NEW)
    assert total >= 1
    assert any(o.id == test_order.id for o in orders)

    # test missing term
    orders, total = await order_service.list_orders(search="MissingTermXYZ")
    assert total == 0


@pytest.mark.asyncio
async def test_dashboard_stats_service(order_service: OrderService, test_order: Order) -> None:
    # ensure it's paid
    await order_service.update_order_status(test_order.id, OrderStatusUpdate(status=OrderStatus.PAID))

    stats = await order_service.get_dashboard_stats()
    assert stats.total_orders >= 1
    assert stats.total_revenue >= Decimal("99.99")
    assert stats.total_tenants >= 1
    assert "paid" in stats.orders_by_status
