from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.core.services.ruleset.ruleset_manager_service import RulesetManagerService
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest
from model.authentication.admin_session_data import AdminSessionData
from utils.auth_utils import authenticate_admin_session

router = APIRouter()

@router.post("/{tenant_id}/ruleset")
async def add_ruleset(
    tenant_id: str, 
    ruleset_request: AddRulesetRequest, 
    admin_session_data: AdminSessionData = Depends(authenticate_admin_session)
):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await RulesetManagerService.add_ruleset(tenant_id=tenant_id,ruleset_request=ruleset_request)

@router.get("/{tenant_id}/ruleset")
async def get_rulesets(
    tenant_id: str,
    summary: bool = Query(False),
    summary_paginated: bool = Query(False),
    name: Optional[str] = Query(None),
    filter_name: Optional[str] = Query(None),
    is_ruleset_enabled: Optional[bool] = Query(None),
    has_injectors: Optional[bool] = Query(None),
    page: int = Query(1),
    page_size: int = Query(10),
    admin_session_data: AdminSessionData = Depends(authenticate_admin_session)
):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin", "Schema Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )

    if summary and summary_paginated:
        raise HTTPException(
            status_code=400,
            detail="Cannot use both 'summary' and 'summary_paginated' query parameters simultaneously."
        )

    if summary:
        return await RulesetManagerService.get_rulesets_summary(tenant_id=tenant_id)

    if summary_paginated:
        # Use the dedicated filter parameter for paginated queries
        effective_filter = filter_name if filter_name is not None else name
        return await RulesetManagerService.get_rulesets_summary_paginated(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            filter_name=effective_filter,
            is_ruleset_enabled=is_ruleset_enabled,
            has_injectors=has_injectors
        )

    if name:
        return await RulesetManagerService.get_ruleset(tenant_id=tenant_id, ruleset_name=name)

    return await RulesetManagerService.get_rulesets(tenant_id=tenant_id)

@router.put("/{tenant_id}/ruleset/{ruleset_name}")
async def update_ruleset(
    tenant_id: str, 
    ruleset_name: str, 
    update_ruleset_request: AddRulesetRequest, 
    admin_session_data: AdminSessionData = Depends(authenticate_admin_session)
):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await RulesetManagerService.update_ruleset(tenant_id=tenant_id, ruleset_name=ruleset_name, update_ruleset_request=update_ruleset_request)

@router.delete("/{tenant_id}/ruleset/{ruleset_name}")
async def delete_ruleset(
    tenant_id: str, 
    ruleset_name: str, 
    admin_session_data: AdminSessionData = Depends(authenticate_admin_session)
):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await RulesetManagerService.delete_ruleset(tenant_id=tenant_id,ruleset_name=ruleset_name)