from fastapi import APIRouter

from api.core.services.ruleset.ruleset_manager_service import RulesetManagerService
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest

router = APIRouter()

@router.post("/ruleset/{tenant_id}")
async def add_ruleset(tenant_id: str, ruleset_request: AddRulesetRequest):
    return await RulesetManagerService.add_ruleset(tenant_id=tenant_id,ruleset_request=ruleset_request)

@router.get("/ruleset/{tenant_id}/{ruleset_name}")
async def get_ruleset(tenant_id: str, ruleset_name: str):
    return await RulesetManagerService.get_ruleset(tenant_id=tenant_id, ruleset_name=ruleset_name)

@router.put("/ruleset/{tenant_id}/{ruleset_name}")
async def update_ruleset(tenant_id: str, ruleset_name: str, update_ruleset_request: AddRulesetRequest):
    return await RulesetManagerService.update_ruleset(tenant_id=tenant_id, ruleset_name=ruleset_name, update_ruleset_request=update_ruleset_request)

@router.delete("/ruleset/{tenant_id}/{ruleset_name}")
async def update_ruleset(tenant_id: str, ruleset_name: str):
    return await RulesetManagerService.delete_ruleset(tenant_id=tenant_id,ruleset_name=ruleset_name)