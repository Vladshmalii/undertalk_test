from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.order_model import OrderStatus


class OrderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    status: OrderStatus = OrderStatus.NEW


class OrderUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    amount: Decimal | None = Field(None, ge=0, decimal_places=2)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    title: str
    amount: Decimal
    status: OrderStatus
    created_at: datetime


class PaginationMeta(BaseModel):
    limit: int
    offset: int
    total: int
    page: int
    total_pages: int


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    meta: PaginationMeta


class DashboardStatsResponse(BaseModel):
    total_orders: int
    total_revenue: Decimal
    orders_by_status: dict[str, int]
    total_tenants: int
