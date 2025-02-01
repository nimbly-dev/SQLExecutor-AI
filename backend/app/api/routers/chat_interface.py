from fastapi import APIRouter, HTTPException, Header, Query

from api.core.services.schema.schema_manager_service import SchemaManagerService
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService;
from api.core.services.external_system.sql_context.sql_context_integration_service import SQLContextIntegrationService;
from api.core.services.external_system.api_context.api_context_integration_service import APIContextIntegrationService;
from api.core.services.external_system.external_session_manager_service import SessionManagerService;
from api.core.services.chat_interface.chat_interface_service import ChatInterfaceService;

from model.tenant.tenant import Tenant;
from model.external_system_integration.external_user_session_data_setting import ExternalSessionDataSetting;
from model.chat_interface.chat_interface_setting import ChatInterfaceSetting;
from model.chat_interface.chat_interface_settings import ChatInterfaceSettings;
from model.external_system_integration.external_user_session_data import ExternalSessionData;
from model.requests.chat_interface.toggle_chat_interface_setting import UpdateChatInterfaceSettingRequest;
from model.requests.chat_interface.toggle_chat_interface_settings import UpdateChatInterfaceSettingsRequest;

router = APIRouter()

@router.get("/{tenant_id}/{schema_name}/users-context")
async def get_users_context(
    tenant_id: str,
    schema_name: str,
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    page_limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    order_direction: str = Query("ASC", regex="^(ASC|DESC)$", description="Sort direction"),
    sort_field: str = Query("email", description="Field to sort by"),
):
    tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    schema = await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=schema_name)
    if not schema:
        raise HTTPException(
            status_code=404,
            detail=f"Schema '{schema_name}' not found for tenant '{tenant_id}'."
        )

    schema_integration = schema.schema_chat_interface_integration
    if not schema_integration or not schema_integration.enabled:
        raise HTTPException(status_code=400, detail="Schema-based chat interface integration is disabled.")

    if schema.context_type not in ["sql", "api"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid or missing context_type in schema settings."
        )

    if not schema_integration.get_contexts_query or not schema_integration.get_contexts_count_query:
        raise HTTPException(
            status_code=400,
            detail="Schema does not define required SQL queries for user context retrieval."
        )

    result = await ChatInterfaceService.get_paginated_context_users_from_context_table(
        tenant=tenant,
        page=page,
        limit=page_limit,
        order_direction=order_direction,
        sort_field=sort_field,
        schema=schema
    )

    total_count = await ChatInterfaceService.get_context_table_count(
        tenant=tenant,
        count_query=schema_integration.get_contexts_count_query,
        schema_name=schema_name
    )

    return {"data": result, "page": page, "limit": page_limit, "total_count": total_count}
    
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