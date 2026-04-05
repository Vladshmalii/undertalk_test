from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_order_service
from app.core.security import get_current_user_id
from app.db.session import get_session
from app.schemas.order_schema import DashboardStatsResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> DashboardStatsResponse:
    service = get_order_service(session)
    return await service.get_dashboard_stats()
