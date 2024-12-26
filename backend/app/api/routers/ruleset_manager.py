from fastapi import APIRouter, Depends

from api.core.services.ruleset.ruleset_manager_service import RulesetManagerService
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest
from model.authentication.admin_session_data import AdminSessionData

from utils.jwt_utils import authenticate_admin_session

router = APIRouter()

@router.post("/ruleset/{tenant_id}")
async def add_ruleset(tenant_id: str, ruleset_request: AddRulesetRequest, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await RulesetManagerService.add_ruleset(tenant_id=tenant_id,ruleset_request=ruleset_request)

@router.get("/ruleset/{tenant_id}/{ruleset_name}")
async def get_ruleset(tenant_id: str, ruleset_name: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await RulesetManagerService.get_ruleset(tenant_id=tenant_id, ruleset_name=ruleset_name)

@router.put("/ruleset/{tenant_id}/{ruleset_name}")
async def update_ruleset(tenant_id: str, ruleset_name: str, update_ruleset_request: AddRulesetRequest, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await RulesetManagerService.update_ruleset(tenant_id=tenant_id, ruleset_name=ruleset_name, update_ruleset_request=update_ruleset_request)

@router.delete("/ruleset/{tenant_id}/{ruleset_name}")
async def update_ruleset(tenant_id: str, ruleset_name: str, _: AdminSessionData = Depends(authenticate_admin_session)):
    return await RulesetManagerService.delete_ruleset(tenant_id=tenant_id,ruleset_name=ruleset_name)