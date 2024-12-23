from fastapi import APIRouter, HTTPException
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from api.core.services.tenant_manager.tenant_settings_service import TenantSettingsService
from model.tenant.tenant import Tenant
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel
from model.requests.tenant_manager.add_setting_to_tenant_request import AddSettingToTenantRequest
from model.requests.tenant_manager.update_setting_to_tenant_request import UpdateSettingRequest

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

# Settings API
@router.post("/settings/{tenant_id}")
async def add_setting(tenant_id: str, settings_request: AddSettingToTenantRequest):
    return await TenantSettingsService.add_settings_to_tenant(tenant_id=tenant_id,add_settings_request=settings_request)

@router.put("/settings/{tenant_id}/{category_key}")
async def update_settings(tenant_id: str,category_key: str ,settings_request: UpdateSettingRequest):
    return await TenantSettingsService.update_cat_settings_to_tenant(tenant_id=tenant_id,category_key=category_key,category_settings=settings_request)

@router.delete("/settings/{tenant_id}/{setting_category}/{setting_key}")
async def delete_settings(tenant_id: str, setting_category: str, setting_key: str):
    return await TenantSettingsService.delete_setting(tenant_id=tenant_id,setting_category=setting_category,setting_key=setting_key)

@router.get("/settings/{tenant_id}")
async def get_settings(tenant_id: str):
    return await TenantSettingsService.get_tenant_settings(tenant_id=tenant_id)

@router.get("/settings/{tenant_id}/{setting_category}/{setting_key}")
async def get_setting_detail(tenant_id: str, setting_category: str, setting_key: str):
    return await TenantSettingsService.get_setting_detail(tenant_id=tenant_id, setting_category=setting_category, setting_key=setting_key)
