from fastapi import APIRouter, HTTPException, Header

from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService;
from api.core.services.external_system.sql_context.sql_context_integration_service import SQLContextIntegrationService;
from api.core.services.external_system.api_context.api_context_integration_service import APIContextIntegrationService;
from api.core.services.external_system.external_session_manager_service import SessionManagerService;
from api.core.services.chat_interface.chat_interface_service import ChatInterfaceService;

from model.exceptions.base_exception_message import BaseExceptionMessage
from model.tenant.tenant import Tenant;
from model.tenant.setting import Setting;
from model.external_system_integration.external_user_session_data_setting import ExternalSessionDataSetting;
from model.chat_interface.chat_interface_setting import ChatInterfaceSetting;
from model.chat_interface.chat_interface_settings import ChatInterfaceSettings;
from model.external_system_integration.external_user_session_data import ExternalSessionData;
from model.requests.chat_interface.toggle_chat_interface_setting import UpdateChatInterfaceSettingRequest;
from model.requests.chat_interface.toggle_chat_interface_settings import UpdateChatInterfaceSettingsRequest;

from utils.tenant_manager.setting_utils import SettingUtils;

from api.core.constants.tenant.settings_categories import (
    SQL_CONTEXT_INTEGRATION,
    API_CONTEXT_INTEGRATION,
    FRONTEND_SANDBOX_CHAT_INTERFACE,
    SQL_INJECTORS
);

router = APIRouter()

@router.get("/{tenant_id}/users-context")
async def get_users_context(tenant_id: str, page: int = 1,page_limit: int = 10 ,order_direction: str = "ASC"):
    """
    Fetch tenant-specific user contexts
    """
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    integration_type = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=FRONTEND_SANDBOX_CHAT_INTERFACE,
        setting_key="CHAT_CONTEXT_INTEGRATION_TYPE"
    )
    chat_custom_fields = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=FRONTEND_SANDBOX_CHAT_INTERFACE,
        setting_key="CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS"
    ) 
    
    if chat_custom_fields is None:
        error_message = BaseExceptionMessage(
            message="CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS setting is not defined."
        ).dict()
        raise HTTPException(status_code=400, detail=error_message)

    if integration_type == "sql":
        sql_context_integration_toggle = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_CONTEXT_INTEGRATION,
            setting_key="SQL_CONTEXT_INTEGRATION_TOGGLE"
        )
        
        if sql_context_integration_toggle == False:
            raise HTTPException(status_code=400, detail="SQL Context Integration is disabled for this tenant")
        
        result = await SQLContextIntegrationService.get_paginated_context_users_from_context_table(
            tenant=tenant,
            page=page,
            limit=page_limit,
            order_direction=order_direction,
            chat_custom_fields=chat_custom_fields
        )

        return {"data": result, "page": page, "limit": page_limit}
    
    elif integration_type == "api":
        api_context_integration_toggle = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=API_CONTEXT_INTEGRATION,
            setting_key="API_CONTEXT_INTEGRATION_TOGGLE"
        )
        
        if api_context_integration_toggle == False:
            raise HTTPException(status_code=400, detail="API Context Integration is disabled for this tenant")
        
        result = await APIContextIntegrationService.call_external_get_users_endpoint(
            tenant=tenant,
            page=page,
            limit=page_limit,
            order_direction=order_direction
        )

        total_count = await APIContextIntegrationService.call_external_get_users_context_counts(tenant=tenant)

        # Filter results of the API call based on the custom fields defined in the setting
        chat_custom_fields_list = eval(chat_custom_fields)
        filtered_result = [
            {
                "user_identifier": user.get("user_identifier"),
                "custom_fields": {
                    key: user.get("custom_fields", {}).get(key) for key in chat_custom_fields_list
                }
            }
            for user in result
        ]
        
        return {"data": filtered_result, "page": page, "limit": page_limit, "total_count": total_count}
        
    raise HTTPException(status_code=400, detail="Unsupported integration type")
    
    
@router.get("/{tenant_id}/{session_id}/chat-interface-settings")
async def get_chat_interface_settings(tenant_id: str, session_id: str):
    """Get chat interface settings

    Args:
        tenant_id (str): Tenant ID of the Tenant
        session_id (str): Session ID of the context user
    """
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    session_data: ExternalSessionData = await SessionManagerService.get_external_session(session_id=session_id)
    
    if session_data is None:
        raise HTTPException(status_code=400, detail="Session ID cannot be found")
    
    chat_interface_settings = ChatInterfaceService.build_chat_interface_settings(tenant=tenant, session_data=session_data)
    
    return {"data": chat_interface_settings.dict()}

@router.patch("/{tenant_id}/{session_id}/chat-interface-settings")
async def update_chat_interface_settings(tenant_id: str, session_id: str, request: UpdateChatInterfaceSettingsRequest):
    """Update the Chat Interface Settings

    Args:
        tenant_id (str): Tenant ID of the Tenant
        session_id (str): Session ID of the context user
    """
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    session_data: ExternalSessionData = await SessionManagerService.get_external_session(session_id=session_id)
    
    if session_data is None:
        raise HTTPException(status_code=400, detail="Session ID cannot be found")
    
    #Apply changes to mongodb
    await ChatInterfaceService.apply_patched_chat_interface_settings_on_mongodb(tenant=tenant,
                                                                                session_data=session_data,
                                                                                patch_request=request)
    
    # Build and return new Chat Interface Settings
    chat_interface_settings = ChatInterfaceService.build_chat_interface_settings(tenant=tenant, session_data=session_data)
    return {"data": chat_interface_settings.dict()}