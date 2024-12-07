from fastapi import APIRouter, HTTPException
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from model.tenant import Tenant
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel

router = APIRouter()

@router.post("/tenants/")
async def add_tenant(tenant: Tenant):
    return await TenantManagerService.add_tenant(tenant)

@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    return await TenantManagerService.get_tenant(tenant_id=tenant_id)

@router.put("/tenants/{tenant_id}")
async def update_tenant(tenant_id: str, tenant_data: UpdateTenantRequestModel):
    return await TenantManagerService.update_tenant(tenant_id=tenant_id, tenant_data=tenant_data)

@router.delete("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    return await TenantManagerService.delete_tenant(tenant_id=tenant_id)