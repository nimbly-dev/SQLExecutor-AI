from fastapi import APIRouter, Depends, HTTPException

from api.core.services.ruleset.ruleset_manager_service import RulesetManagerService
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest
from model.authentication.admin_session_data import AdminSessionData

from utils.jwt_utils import authenticate_admin_session

router = APIRouter()

@router.post("/{tenant_id}/ruleset")
async def add_ruleset(tenant_id: str, ruleset_request: AddRulesetRequest, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await RulesetManagerService.add_ruleset(tenant_id=tenant_id,ruleset_request=ruleset_request)

@router.get("/{tenant_id}/ruleset/{ruleset_name}")
async def get_ruleset(tenant_id: str, ruleset_name: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await RulesetManagerService.get_ruleset(tenant_id=tenant_id, ruleset_name=ruleset_name)

@router.put("/{tenant_id}/ruleset/{ruleset_name}")
async def update_ruleset(tenant_id: str, ruleset_name: str, update_ruleset_request: AddRulesetRequest, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await RulesetManagerService.update_ruleset(tenant_id=tenant_id, ruleset_name=ruleset_name, update_ruleset_request=update_ruleset_request)

@router.delete("/{tenant_id}/ruleset/{ruleset_name}")
async def update_ruleset(tenant_id: str, ruleset_name: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Ruleset Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await RulesetManagerService.delete_ruleset(tenant_id=tenant_id,ruleset_name=ruleset_name)