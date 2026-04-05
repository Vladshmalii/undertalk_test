from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repository import OrderRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.order_service import OrderService
from app.services.tenant_service import TenantService


def get_tenant_service(session: AsyncSession) -> TenantService:
    repository = TenantRepository(session)
    return TenantService(repository)


def get_order_service(session: AsyncSession) -> OrderService:
    order_repository = OrderRepository(session)
    tenant_repository = TenantRepository(session)
    return OrderService(order_repository, tenant_repository)
