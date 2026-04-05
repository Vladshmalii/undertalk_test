from datetime import date
from uuid import UUID

from fastapi import HTTPException, status

from app.core.logging import get_logger
from app.models.order_model import Order, OrderStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.tenant_repository import TenantRepository
from app.schemas.order_schema import DashboardStatsResponse, OrderCreate, OrderStatusUpdate, OrderUpdate

logger = get_logger(__name__)


class OrderService:
    def __init__(self, order_repository: OrderRepository, tenant_repository: TenantRepository) -> None:
        self._order_repository = order_repository
        self._tenant_repository = tenant_repository

    async def _verify_tenant(self, tenant_id: UUID) -> None:
        exists = await self._tenant_repository.exists(tenant_id)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant {tenant_id} not found",
            )

    async def create_order(self, tenant_id: UUID, data: OrderCreate) -> Order:
        await self._verify_tenant(tenant_id)
        logger.info("creating_order", tenant_id=str(tenant_id), title=data.title)
        order = await self._order_repository.create(
            tenant_id=tenant_id,
            title=data.title,
            amount=data.amount,
            status=data.status,
        )
        logger.info("order_created", order_id=str(order.id), tenant_id=str(tenant_id))
        return order

    async def get_order(self, order_id: UUID) -> Order:
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )
        return order

    async def list_orders(
        self,
        tenant_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
        status_filter: OrderStatus | None = None,
        search: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[Order], int]:
        if tenant_id:
            await self._verify_tenant(tenant_id)

        orders = await self._order_repository.get_all(
            limit=limit,
            offset=offset,
            tenant_id=tenant_id,
            status=status_filter,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
        total = await self._order_repository.count(
            tenant_id=tenant_id,
            status=status_filter,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
        return orders, total

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> Order:
        order = await self._order_repository.update(order_id, **data.model_dump(exclude_unset=True))
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )
        logger.info("order_updated", order_id=str(order_id))
        return order

    async def update_order_status(self, order_id: UUID, data: OrderStatusUpdate) -> Order:
        order = await self._order_repository.update(order_id, status=data.status)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )
        logger.info("order_status_updated", order_id=str(order_id), new_status=data.status)
        return order

    async def delete_order(self, order_id: UUID) -> None:
        deleted = await self._order_repository.delete(order_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )
        logger.info("order_deleted", order_id=str(order_id))

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        stats = await self._order_repository.get_dashboard_stats()
        return DashboardStatsResponse.model_validate(stats)
