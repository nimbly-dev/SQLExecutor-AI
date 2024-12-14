from fastapi import APIRouter, Depends, HTTPException

from api.core.services.llm_wrapper.llm_service_wrapper import LLMServiceWrapper
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from api.core.resolvers.query_scope.query_scope_resolver import QueryScopeResolver

from model.tenant import Tenant
from model.schema import Schema
from model.requests.sql_generation.user_input_request import UserInputRequest

from utils.jwt_utils import authenticate_session


router = APIRouter()


@router.post("/{tenant_id}")
async def generate_sql(tenant_id: str, user_request: UserInputRequest, session: dict = Depends(authenticate_session)):
    # Fetch tenant details
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    user_query_scope = await LLMServiceWrapper.get_query_scope_using_default_mode(
        user_input=user_request
    )

    query_scope_resolver = QueryScopeResolver(
        session_data=session,
        settings=tenant.settings,
        query_scope=user_query_scope
    )
    
    matched_schema: Schema =  await query_scope_resolver.match_user_query_to_schema(tenant_id=tenant_id)

    # Use the new resolve_matched_schema method
    return matched_schema
    