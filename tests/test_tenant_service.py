import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant_model import Tenant
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant_schema import TenantCreate, TenantUpdate
from app.services.tenant_service import TenantService


@pytest_asyncio.fixture
async def tenant_service(db_session: AsyncSession) -> TenantService:
    repo = TenantRepository(db_session)
    return TenantService(repo)


@pytest.mark.asyncio
async def test_create_tenant_service(tenant_service: TenantService) -> None:
    data = TenantCreate(name="Service Company")
    tenant_resp = await tenant_service.create_tenant(data)
    assert tenant_resp.name == "Service Company"
    assert tenant_resp.id is not None
    assert tenant_resp.orders_count == 0


@pytest.mark.asyncio
async def test_get_tenant_service(tenant_service: TenantService, test_tenant: Tenant) -> None:
    tenant_resp = await tenant_service.get_tenant(test_tenant.id)
    assert tenant_resp.id == test_tenant.id
    assert tenant_resp.name == test_tenant.name


@pytest.mark.asyncio
async def test_update_tenant_service(tenant_service: TenantService, test_tenant: Tenant) -> None:
    data = TenantUpdate(name="Updated Service LLC")
    tenant_resp = await tenant_service.update_tenant(test_tenant.id, data)
    assert tenant_resp.name == "Updated Service LLC"

    # Verify the update is readable
    check = await tenant_service.get_tenant(test_tenant.id)
    assert check.name == "Updated Service LLC"


@pytest.mark.asyncio
async def test_delete_tenant_service(tenant_service: TenantService, test_tenant: Tenant) -> None:
    await tenant_service.delete_tenant(test_tenant.id)

    with pytest.raises(Exception) as exc_info:
        await tenant_service.get_tenant(test_tenant.id)
    assert "not found" in str(exc_info.value).lower()
