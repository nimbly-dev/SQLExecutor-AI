from fastapi import APIRouter

from api.core.services.authentication.external_jwt_authentication_service_wrapper import ExternalJWTAuthorizationServiceWrapper
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from api.core.services.authentication.external_session_manager_service import SessionManagerService
from model.requests.authentication.auth_login_request import AuthLoginRequest
from model.authentication.external_user_decoded_jwt_token import DecodedJwtToken
from model.tenant.tenant import Tenant

router = APIRouter()

@router.post("/login")
async def login_external_user(login_request: AuthLoginRequest):
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=login_request.auth_tenant_id)
    
    response_user_token = await ExternalJWTAuthorizationServiceWrapper.call_external_login(tenant=tenant,auth_request=login_request)
    decoded_token: DecodedJwtToken = ExternalJWTAuthorizationServiceWrapper.decode_json_token(tenant=tenant,user_token=response_user_token)
    session_data = await SessionManagerService.create_jwt_session(decoded_jwt_token=decoded_token, tenant= tenant)
    return session_data


@router.post("/logout/{session_id}")
async def logout_external_user(session_id: str):
    return await SessionManagerService.delete_jwt_session(session_id=session_id)