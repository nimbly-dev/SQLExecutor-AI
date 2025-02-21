from fastapi import APIRouter, HTTPException, Header

from api.core.services.schema.schema_manager_service import SchemaManagerService
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService;
from api.core.services.external_system.api_context.api_context_integration_service import APIContextIntegrationService;
from api.core.services.external_system.external_session_manager_service import SessionManagerService;

from model.requests.external_system_integration.fetch_external_context_request import CreateExternalSessionRequest;
from model.requests.external_system_integration.invalidate_external_session_request import InvalidateExternalSession;
from model.authentication.external_user_decoded_jwt_token import DecodedJwtToken
from model.schema.schema import Schema
from model.tenant.tenant import Tenant

router = APIRouter()

@router.post("/{tenant_id}/create-context-session")
async def create_external_session(tenant_id: str,
                                  request: CreateExternalSessionRequest, 
                                  x_api_key: str = Header(...)):
    """
    Create External Context-Aware Session from External System Context Table
    """
    print("I am here")
    # Fetch Tenant and Schema using their respective services
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    schema: Schema = await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=request.schema_name)

    # Ensure that API Context Settings are available in the Schema
    api_context = schema.context_setting.api_context
    if not api_context:
        raise HTTPException(status_code=400, detail="API context settings are not defined for the schema.")

    # Call the external get-user endpoint with the necessary context
    
    try:
        response_user_token = await APIContextIntegrationService.call_external_get_user_endpoint(
            tenant=tenant,
            api_context=api_context,
            request=request
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=424, detail=f"Failed to fetch user context from external system: {str(e)}")
        
    print("I am here 2")

    # Decode the received JWT token
    decoded_token: DecodedJwtToken = APIContextIntegrationService.decode_json_token(
        tenant=tenant,
        user_token=response_user_token
    )
    
    # Create the external session using the Session Manager Service
    session_data = await SessionManagerService.create_external_session(
        tenant, 
        request.context_user_identifier_value, 
        decoded_token.custom_fields
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