from fastapi import APIRouter, Depends
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from api.core.services.tenant_manager.tenant_settings_service import TenantSettingsService
from api.core.services.tenant_manager.admin_user_manager_service import AdminUserService
from model.authentication.admin_session_data import AdminSessionData

from utils.jwt_utils import authenticate_admin_session
from model.tenant.tenant import Tenant
from model.authentication.admin_user import AdminUser
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel
from model.requests.tenant_manager.add_setting_to_tenant_request import AddSettingToTenantRequest
from model.requests.tenant_manager.update_setting_to_tenant_request import UpdateSettingRequest

router = APIRouter()

@router.post("/tenants/")
async def add_tenant(tenant: Tenant):
    return await TenantManagerService.add_tenant(tenant)

@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantManagerService.get_tenant(tenant_id=tenant_id)

@router.put("/tenants/{tenant_id}")
async def update_tenant(tenant_id: str, tenant_data: UpdateTenantRequestModel, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantManagerService.update_tenant(tenant_id=tenant_id, tenant_data=tenant_data)

@router.delete("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantManagerService.delete_tenant(tenant_id=tenant_id)

# Settings API
@router.post("/settings/{tenant_id}")
async def add_setting(tenant_id: str, settings_request: AddSettingToTenantRequest, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantSettingsService.add_settings_to_tenant(tenant_id=tenant_id,add_settings_request=settings_request)

@router.put("/settings/{tenant_id}/{category_key}")
async def update_settings(tenant_id: str,category_key: str ,settings_request: UpdateSettingRequest, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantSettingsService.update_cat_settings_to_tenant(tenant_id=tenant_id,category_key=category_key,category_settings=settings_request)

@router.delete("/settings/{tenant_id}/{setting_category}/{setting_key}")
async def delete_settings(tenant_id: str, setting_category: str, setting_key: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantSettingsService.delete_setting(tenant_id=tenant_id,setting_category=setting_category,setting_key=setting_key)

@router.get("/settings/{tenant_id}")
async def get_settings(tenant_id: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantSettingsService.get_tenant_settings(tenant_id=tenant_id)

@router.get("/settings/{tenant_id}/{setting_category}/{setting_key}")
async def get_setting_detail(tenant_id: str, setting_category: str, setting_key: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await TenantSettingsService.get_setting_detail(tenant_id=tenant_id, setting_category=setting_category, setting_key=setting_key)

# User Admin API
@router.post("/user-admin/{tenant_id}")
async def add_admin(tenant_id: str, add_admin_request: AdminUser, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await AdminUserService.add_admin(tenant_id=tenant_id, admin=add_admin_request)

@router.put("/user-admin/{tenant_id}/{admin_user_id}")
async def update_admin(tenant_id: str,admin_user_id: str , update_admin: AdminUser, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await AdminUserService.update_admin(tenant_id=tenant_id, user_id=admin_user_id ,update_admin=update_admin)

@router.delete("/user-admin/{tenant_id}/{admin_user_id}")
async def delete_admin(tenant_id: str, admin_user_id: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await AdminUserService.delete_admin(tenant_id=tenant_id, user_id=admin_user_id)

@router.get("/user-admin/{tenant_id}")
async def get_admins(tenant_id: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await AdminUserService.get_admins(tenant_id=tenant_id)

@router.get("/user-admin/{tenant_id}/{admin_user_id}")
async def get_admins(tenant_id: str, admin_user_id: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await AdminUserService.get_admin(tenant_id=tenant_id, user_id=admin_user_id)