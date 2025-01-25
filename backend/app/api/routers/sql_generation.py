import logging
from fastapi import APIRouter, Depends, HTTPException

from api.core.services.llm_wrapper.llm_service_wrapper import LLMServiceWrapper
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from api.core.services.sql_runner.sql_runner_service import SqlRunnerService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from api.core.services.ruleset.ruleset_manager_service import RulesetManagerService
from api.core.resolvers.query_scope.query_scope_resolver import QueryScopeResolver
from api.core.resolvers.access_control.user_access_control_resolver import AccessControlResolver
from api.core.resolvers.schema.schema_resolver import SchemaResolver
from api.core.resolvers.access_control.injector_resolver import InjectorResolver

from model.tenant.tenant import Tenant
from model.schema.schema import Schema
from model.ruleset.ruleset import Ruleset
from model.requests.sql_generation.user_input_request import UserInputRequest
from model.external_system_integration.external_user_session_data import ExternalSessionData
from model.responses.sql_generation.sql_generation_response import SqlGenerationResponse

from utils.auth_utils import authenticate_session
from utils.ruleset.ruleset_utils import extract_ruleset_name
from utils.tenant_manager.setting_utils import SettingUtils

from api.core.constants.tenant.settings_categories import SQL_INJECTORS

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{tenant_id}")
async def generate_sql(tenant_id: str, 
                       user_request: UserInputRequest, 
                       run_sql: bool = True, 
                       session: ExternalSessionData = Depends(authenticate_session)):
    # Fetch tenant details
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    user_query_scope = await LLMServiceWrapper.get_query_scope_using_default_mode(
        user_input=user_request
    )
    query_scope_resolver = QueryScopeResolver(
        session_data=session,
        settings=tenant.settings,
        query_scope=user_query_scope,
        tenant=tenant
    )
    injector_enabled = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=SQL_INJECTORS,
        setting_key="DYNAMIC_INJECTION"
    )

    try:
        matched_schema: Schema = await query_scope_resolver.match_user_query_to_schema(tenant_id=tenant_id)
        resolved_user_query_scope = query_scope_resolver.resolve_query_scope(matched_schema=matched_schema)
    except HTTPException as e:
        logger.error(f"QueryScope Resolution Failed: {e.detail}")
        logger.info(f"Original Query Scope: {user_query_scope.dict()}")
        raise e
    
    # Get ruleset from Schema, currently PoC supports only single ruleset.
    matched_ruleset_name = extract_ruleset_name(ruleset_placeholder=matched_schema.filter_rules[0])
    matched_ruleset: Ruleset = await RulesetManagerService.get_ruleset(tenant_id=tenant_id, ruleset_name=matched_ruleset_name)
    
    access_resolver = AccessControlResolver(session_data=session, ruleset=matched_ruleset, matched_schema=matched_schema)
    schema_resolver = SchemaResolver(session_data=session, tenant=tenant, matched_schema=matched_schema, query_scope=resolved_user_query_scope)
    
    access_resolver.has_access_to_scope(resolved_user_query_scope)
    
    generated_sql = await LLMServiceWrapper.generate_sql_query(
        user_input=user_request,
        resolved_schema=schema_resolver.resolve_schema()
    )

    # Apply injectors if enabled
    updated_sql = generated_sql
    injected_str = None
    if injector_enabled:
        injector_resolver = InjectorResolver(session_data=session, ruleset=matched_ruleset)
        updated_sql, injected_str = injector_resolver.apply_injectors(
            sql_query=generated_sql,
            tenant=tenant
        )

    # Run SQL if specified
    run_sql_result = None
    if run_sql:
        try:
            run_sql_result = SqlRunnerService.run_sql(
                orginal_user_input=user_request.input,
                query_scope=resolved_user_query_scope,
                query=updated_sql, 
                tenant=tenant, params={}
            )
        except HTTPException as e:
            logger.error(f"SQL Execution Failed: {e.detail}")
            logger.info(f"Original Query Scope: {user_query_scope.dict()}")
            raise e

    # Construct the response
    sql_generation_response = SqlGenerationResponse(
        query_scope=resolved_user_query_scope,
        user_input=user_request.input,
        sql_query=updated_sql,
        sql_response=run_sql_result,
        injected_str=injected_str
    )
    
    return sql_generation_response
    
@router.post("/{tenant_id}/{schema_name}")
async def generate_sql_given_schema(tenant_id: str, schema_name: str, 
                                    user_request: UserInputRequest, run_sql: bool = True,
                                    session: ExternalSessionData = Depends(authenticate_session)):
    # Fetch tenant and schema details
    tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    schema: Schema = await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=schema_name)
    
    # Resolve query scope
    user_query_scope = await LLMServiceWrapper.get_query_scope_using_default_mode(
        user_input=user_request
    )
    query_scope_resolver = QueryScopeResolver(
        session_data=session,
        settings=tenant.settings,
        query_scope=user_query_scope,
        tenant=tenant
    )
    injector_enabled = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=SQL_INJECTORS,
        setting_key="DYNAMIC_INJECTION"
    )

    try:
        resolved_user_query_scope = query_scope_resolver.resolve_query_scope(matched_schema=schema)
    except HTTPException as e:
        logger.error(f"QueryScope Resolution Failed: {e.detail}")
        logger.info(f"Original Query Scope: {user_query_scope.dict()}")
        raise e
    
    # Get ruleset from Schema
    matched_ruleset_name = extract_ruleset_name(ruleset_placeholder=schema.filter_rules[0])
    matched_ruleset: Ruleset = await RulesetManagerService.get_ruleset(tenant_id=tenant_id, ruleset_name=matched_ruleset_name)
    
    access_resolver = AccessControlResolver(session_data=session, ruleset=matched_ruleset, matched_schema=schema)
    schema_resolver = SchemaResolver(session_data=session, tenant=tenant, matched_schema=schema, query_scope=resolved_user_query_scope)
    
    access_resolver.has_access_to_scope(resolved_user_query_scope)
    
    generated_sql = await LLMServiceWrapper.generate_sql_query(
        user_input=user_request,
        resolved_schema=schema_resolver.resolve_schema()
    )

    # Apply injectors if enabled
    updated_sql = generated_sql
    injected_str = None
    if injector_enabled:
        injector_resolver = InjectorResolver(session_data=session, ruleset=matched_ruleset)
        updated_sql, injected_str = injector_resolver.apply_injectors(
            sql_query=generated_sql,
            tenant=tenant
        )

    # Run SQL if specified
    run_sql_result = None
    if run_sql:
        try:
            run_sql_result = SqlRunnerService.run_sql(
                orginal_user_input=user_request.input,
                query_scope=resolved_user_query_scope,
                query=updated_sql, 
                tenant=tenant, 
                params={}
            )
        except HTTPException as e:
            logger.error(f"SQL Execution Failed: {e.detail}")
            logger.info(f"Original Query Scope: {user_query_scope.dict()}")
            raise e

    # Construct the response
    sql_generation_response = SqlGenerationResponse(
        query_scope=resolved_user_query_scope,
        user_input=user_request.input,
        sql_query=updated_sql,
        sql_response=run_sql_result,
        injected_str=injected_str
    )
    
    return sql_generation_response