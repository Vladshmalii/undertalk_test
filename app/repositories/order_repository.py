from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import String, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order_model import Order, OrderStatus
from app.models.tenant_model import Tenant


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _apply_filters(
        self,
        stmt,
        tenant_id: UUID | None = None,
        status: OrderStatus | None = None,
        search: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ):
        if tenant_id is not None:
            stmt = stmt.where(Order.tenant_id == tenant_id)
        if status is not None:
            stmt = stmt.where(Order.status == status)
        if search:
            stmt = stmt.where(Order.title.ilike(f"%{search}%"))
        if date_from:
            stmt = stmt.where(func.date(Order.created_at) >= date_from)
        if date_to:
            stmt = stmt.where(func.date(Order.created_at) <= date_to)
        return stmt

    async def create(self, tenant_id: UUID, title: str, amount: float, status: OrderStatus = OrderStatus.NEW) -> Order:
        order = Order(
            tenant_id=tenant_id,
            title=title,
            amount=amount,
            status=status,
        )
        self._session.add(order)
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def get_by_id(self, order_id: UUID) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        tenant_id: UUID | None = None,
        status: OrderStatus | None = None,
        search: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Order]:
        stmt = select(Order)
        stmt = self._apply_filters(stmt, tenant_id, status, search, date_from, date_to)
        stmt = stmt.order_by(Order.created_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        tenant_id: UUID | None = None,
        status: OrderStatus | None = None,
        search: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Order)
        stmt = self._apply_filters(stmt, tenant_id, status, search, date_from, date_to)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(self, order_id: UUID, **kwargs) -> Order | None:
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if not update_data:
            return await self.get_by_id(order_id)

        stmt = update(Order).where(Order.id == order_id).values(**update_data).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            await self._session.flush()
        return order

    async def delete(self, order_id: UUID) -> bool:
        stmt = delete(Order).where(Order.id == order_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_dashboard_stats(self) -> dict:
        orders_count = await self._session.scalar(select(func.count()).select_from(Order))
        total_revenue = await self._session.scalar(
            select(func.coalesce(func.sum(Order.amount), Decimal(0))).where(Order.status == OrderStatus.PAID)
        )
        tenants_count = await self._session.scalar(select(func.count()).select_from(Tenant))

        # Status distribution
        status_stmt = select(func.cast(Order.status, String), func.count()).group_by(Order.status)
        status_result = await self._session.execute(status_stmt)
        status_dict = {row[0]: row[1] for row in status_result.all()}

        return {
            "total_orders": orders_count or 0,
            "total_revenue": total_revenue or Decimal(0),
            "orders_by_status": status_dict,
            "total_tenants": tenants_count or 0,
        }
