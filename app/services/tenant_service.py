from uuid import UUID

from fastapi import HTTPException, status

from app.core.logging import get_logger
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant_schema import TenantCreate, TenantResponse, TenantUpdate

logger = get_logger(__name__)


class TenantService:
    def __init__(self, repository: TenantRepository) -> None:
        self._repository = repository

    async def create_tenant(self, data: TenantCreate) -> TenantResponse:
        exists = await self._repository.get_by_name(data.name)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this name already exists",
            )
        logger.info("creating_tenant", name=data.name)
        tenant = await self._repository.create(name=data.name)
        logger.info("tenant_created", tenant_id=str(tenant.id))
        return TenantResponse.model_validate(tenant)

    async def get_tenant(self, tenant_id: UUID) -> TenantResponse:
        row = await self._repository.get_by_id(tenant_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant {tenant_id} not found",
            )
        tenant, count = row
        obj = TenantResponse.model_validate(tenant).model_dump()
        obj["orders_count"] = count
        return TenantResponse(**obj)

    async def list_tenants(self, limit: int = 100, offset: int = 0) -> tuple[list[TenantResponse], int]:
        rows = await self._repository.get_all(limit=limit, offset=offset)
        total = await self._repository.count()
        results = []
        for tenant, count in rows:
            obj = TenantResponse.model_validate(tenant).model_dump()
            obj["orders_count"] = count
            results.append(TenantResponse(**obj))
        return results, total

    async def update_tenant(self, tenant_id: UUID, data: TenantUpdate) -> TenantResponse:
        if data.name:
            existing = await self._repository.get_by_name(data.name)
            if existing and existing.id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tenant with this name already exists",
                )

        tenant = await self._repository.update(tenant_id, **data.model_dump(exclude_unset=True))
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant {tenant_id} not found",
            )
        logger.info("tenant_updated", tenant_id=str(tenant_id))

        # We need orders count for the response, fetch it cleanly.
        return await self.get_tenant(tenant_id)

    async def delete_tenant(self, tenant_id: UUID) -> None:
        deleted = await self._repository.delete(tenant_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant {tenant_id} not found",
            )
        logger.info("tenant_deleted", tenant_id=str(tenant_id))
