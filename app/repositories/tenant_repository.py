from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order_model import Order
from app.models.tenant_model import Tenant


class TenantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, name: str) -> Tenant:
        tenant = Tenant(name=name)
        self._session.add(tenant)
        await self._session.flush()
        await self._session.refresh(tenant)
        return tenant

    async def get_by_name(self, name: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, tenant_id: UUID) -> tuple[Tenant, int] | None:
        stmt = (
            select(Tenant, func.count(Order.id).label("orders_count"))
            .outerjoin(Order, Order.tenant_id == Tenant.id)
            .where(Tenant.id == tenant_id)
            .group_by(Tenant.id)
        )
        result = await self._session.execute(stmt)
        return result.first()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[tuple[Tenant, int]]:
        stmt = (
            select(Tenant, func.count(Order.id).label("orders_count"))
            .outerjoin(Order, Order.tenant_id == Tenant.id)
            .group_by(Tenant.id)
            .order_by(Tenant.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(Tenant)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(self, tenant_id: UUID, **kwargs) -> Tenant | None:
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if not update_data:
            return await self.get_by_id(tenant_id)

        stmt = update(Tenant).where(Tenant.id == tenant_id).values(**update_data).returning(Tenant)
        result = await self._session.execute(stmt)
        tenant = result.scalar_one_or_none()
        if tenant:
            await self._session.flush()
        return tenant

    async def delete(self, tenant_id: UUID) -> bool:
        stmt = delete(Tenant).where(Tenant.id == tenant_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, tenant_id: UUID) -> bool:
        stmt = select(func.count()).select_from(Tenant).where(Tenant.id == tenant_id)
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0
