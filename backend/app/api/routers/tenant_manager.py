from fastapi import APIRouter, Depends, HTTPException
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from api.core.services.tenant_manager.tenant_settings_service import TenantSettingsService
from api.core.services.tenant_manager.admin_user_manager_service import AdminUserService
from model.authentication.admin_session_data import AdminSessionData

from utils.auth_utils import authenticate_admin_session
from model.tenant.tenant import Tenant
from model.authentication.admin_user import AdminUser
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel
from model.requests.tenant_manager.add_setting_to_tenant_request import AddSettingToTenantRequest
from model.requests.tenant_manager.update_setting_to_tenant_request import UpdateSettingRequest

router = APIRouter()

@router.post("/")
async def add_tenant(tenant: Tenant):
    return await TenantManagerService.add_tenant(tenant)

@router.get("/{tenant_id}")
async def get_tenant(tenant_id: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantManagerService.get_tenant(tenant_id=tenant_id)

@router.put("/{tenant_id}")
async def update_tenant(tenant_id: str, tenant_data: UpdateTenantRequestModel, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantManagerService.update_tenant(tenant_id=tenant_id, tenant_data=tenant_data)

@router.delete("/{tenant_id}")
async def get_tenant(tenant_id: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantManagerService.delete_tenant(tenant_id=tenant_id)

# Settings API
@router.post("/{tenant_id}/settings")
async def add_setting(tenant_id: str, settings_request: AddSettingToTenantRequest, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantSettingsService.add_settings_to_tenant(tenant_id=tenant_id,add_settings_request=settings_request)

@router.put("/{tenant_id}/settings/{category_key}")
async def update_settings(tenant_id: str,category_key: str ,settings_request: UpdateSettingRequest, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantSettingsService.update_cat_settings_to_tenant(tenant_id=tenant_id,category_key=category_key,category_settings=settings_request)

@router.delete("/{tenant_id}/settings/{setting_category}/{setting_key}")
async def delete_settings(tenant_id: str, setting_category: str, setting_key: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantSettingsService.delete_setting(tenant_id=tenant_id,setting_category=setting_category,setting_key=setting_key)

@router.get("/{tenant_id}/settings")
async def get_settings(tenant_id: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantSettingsService.get_tenant_settings(tenant_id=tenant_id)

@router.get("/{tenant_id}/settings/{setting_category}/{setting_key}")
async def get_setting_detail(tenant_id: str, setting_category: str, setting_key: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await TenantSettingsService.get_setting_detail(tenant_id=tenant_id, setting_category=setting_category, setting_key=setting_key)

# User Admin API
@router.post("/{tenant_id}/user-admin")
async def add_admin(tenant_id: str, add_admin_request: AdminUser, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await AdminUserService.add_admin(tenant_id=tenant_id, admin=add_admin_request)

@router.put("/{tenant_id}/user-admin/{admin_user_id}")
async def update_admin(tenant_id: str,admin_user_id: str , update_admin: AdminUser, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await AdminUserService.update_admin(tenant_id=tenant_id, user_id=admin_user_id ,update_admin=update_admin)

@router.delete("/{tenant_id}/user-admin/{admin_user_id}")
async def delete_admin(tenant_id: str, admin_user_id: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await AdminUserService.delete_admin(tenant_id=tenant_id, user_id=admin_user_id)

@router.get("/{tenant_id}/user-admin")
async def get_admins(tenant_id: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await AdminUserService.get_admins(tenant_id=tenant_id)

@router.get("/{tenant_id}/user-admin/{admin_user_id}")
async def get_admins(tenant_id: str, admin_user_id: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await AdminUserService.get_admin(tenant_id=tenant_id, user_id=admin_user_id)