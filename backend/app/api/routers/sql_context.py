from fastapi import APIRouter, HTTPException, Header

from api.core.constants.tenant.settings_categories import EXTERNAL_SYSTEM_DB_SETTING
from api.core.services.external_system.sql_context.sql_context_integration_service import SQLContextIntegrationService;
from api.core.services.schema.schema_manager_service import SchemaManagerService
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService;
from api.core.services.external_system.external_session_manager_service import SessionManagerService;

from model.requests.external_system_integration.fetch_external_context_request import CreateExternalSessionRequest;
from model.requests.external_system_integration.invalidate_external_session_request import InvalidateExternalSession;
from model.requests.external_system_integration.fetch_external_session_request import FetchExternalSession
from utils.tenant_manager.setting_utils import SettingUtils;

router = APIRouter()

@router.post("/{tenant_id}/create-context-session")
async def create_external_session(
    tenant_id: str,
    request: CreateExternalSessionRequest,
    x_api_key: str = Header(...),
):
    """Create External Context-Aware Session from External System Context Table"""
    tenant = await TenantManagerService.get_tenant(tenant_id)
    schema = await SchemaManagerService.get_schema(tenant_id, request.schema_name)

    if schema.context_setting.sql_context is None:
        raise HTTPException(
            status_code=400,
            detail=f"Schema '{request.schema_name}' does not have an SQL context configured."
        )
    
    sql_context = schema.context_setting.sql_context
    sql_flavor = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=EXTERNAL_SYSTEM_DB_SETTING,
        setting_key="EXTERNAL_TENANT_DB_DIALECT"
    )

    custom_field_values = await SQLContextIntegrationService.get_custom_fields_from_context_table(
        tenant=tenant,
        context_table=sql_context.table,
        user_identifier_field=sql_context.user_identifier,
        user_identifier_value=request.context_user_identifier_value,
        custom_fields=sql_context.custom_fields,
        sql_flavor=sql_flavor,
        custom_get_context_query=sql_context.custom_get_context_query,
        schema_name=request.schema_name
    )

    if custom_field_values is None:
        raise HTTPException(
            status_code=404,
            detail="Context User Identifier cannot be found in the context table."
        )

    session_data = await SessionManagerService.create_external_session(
        tenant=tenant,
        context_user_identifier=request.context_user_identifier_value,
        custom_fields=custom_field_values,
    )

    return session_data
    

@router.delete("/{tenant_id}/invalidate-context-session")
async def invalidate_external_session(tenant_id:str,
                                     request: InvalidateExternalSession, 
                                     x_api_key: str = Header(...),):
    """Invalidate External Context Session using external session_id"""    
    _ = await TenantManagerService.get_tenant(tenant_id)
    
    isSuccesful: bool =  await SessionManagerService.delete_external_session(request.external_session_id)

    if not isSuccesful:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session invalidated successfully", "external_session_id": request.external_session_id}
    
    
@router.get("/{tenant_id}/fetch-context-session")
async def fetch_context_session(tenant_id: str,
                                external_session_id: str,
                                x_api_key: str = Header(...),):
    """Fetch External Context Session using external session_id"""
    session_data = await SessionManagerService.get_external_session(external_session_id)
    
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data