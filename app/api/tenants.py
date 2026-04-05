from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_order_service, get_tenant_service
from app.core.security import get_current_user_id
from app.db.session import get_session
from app.models.order_model import OrderStatus
from app.schemas.order_schema import OrderCreate, OrderListResponse, OrderResponse
from app.schemas.tenant_schema import TenantCreate, TenantListResponse, TenantResponse, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TenantResponse:
    service = get_tenant_service(session)
    return await service.create_tenant(data)


@router.get("", response_model=TenantListResponse)
async def list_tenants(
    current_user_id: UUID = Depends(get_current_user_id),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> TenantListResponse:
    service = get_tenant_service(session)
    tenants, total = await service.list_tenants(limit=limit, offset=offset)
    return TenantListResponse(
        items=tenants,
        meta={
            "limit": limit,
            "offset": offset,
            "total": total,
            "page": (offset // limit) + 1,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        },
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TenantResponse:
    service = get_tenant_service(session)
    return await service.get_tenant(tenant_id)


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> TenantResponse:
    service = get_tenant_service(session)
    return await service.update_tenant(tenant_id, data)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    service = get_tenant_service(session)
    await service.delete_tenant(tenant_id)


# Nested Order Routes


@router.post("/{tenant_id}/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant_order(
    tenant_id: UUID,
    data: OrderCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    service = get_order_service(session)
    order = await service.create_order(tenant_id, data)
    return OrderResponse.model_validate(order)


@router.get("/{tenant_id}/orders", response_model=OrderListResponse)
async def list_tenant_orders(
    tenant_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, description="Search by title"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> OrderListResponse:
    service = get_order_service(session)
    orders, total = await service.list_orders(
        limit=limit,
        offset=offset,
        tenant_id=tenant_id,
        status_filter=status_filter,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )
    return OrderListResponse(
        items=[OrderResponse.model_validate(o) for o in orders],
        meta={
            "limit": limit,
            "offset": offset,
            "total": total,
            "page": (offset // limit) + 1,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        },
    )
