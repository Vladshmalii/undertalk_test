from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class TenantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    orders_count: int = 0


class PaginationMeta(BaseModel):
    limit: int
    offset: int
    total: int
    page: int
    total_pages: int


class TenantListResponse(BaseModel):
    items: list[TenantResponse]
    meta: PaginationMeta
