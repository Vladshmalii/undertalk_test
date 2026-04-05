from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_order_service
from app.core.security import get_current_user_id
from app.db.session import get_session
from app.models.order_model import OrderStatus
from app.schemas.order_schema import OrderListResponse, OrderResponse, OrderStatusUpdate, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderListResponse)
async def list_orders(
    current_user_id: UUID = Depends(get_current_user_id),
    tenant_id: UUID | None = Query(default=None),
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


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    service = get_order_service(session)
    order = await service.get_order(order_id)
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    service = get_order_service(session)
    order = await service.update_order(order_id, data)
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> OrderResponse:
    service = get_order_service(session)
    order = await service.update_order_status(order_id, data)
    return OrderResponse.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> None:
    service = get_order_service(session)
    await service.delete_order(order_id)
