from utils.database import mongodb
from fastapi import HTTPException
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from typing import Union, List
from model.ruleset.ruleset_model import Ruleset
from model.tenant.tenant import Tenant
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest
from model.responses.ruleset_manager.ruleset_response import RulesetResponse

from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService

class RulesetManagerService:

    @staticmethod
    async def create_indexes():
        # Enforce uniqueness on the schema_name field within the same tenant
        collection_schema = mongodb.db["rulesets"]
        collection_schema.create_index([("tenant_id", ASCENDING), ("ruleset_name", ASCENDING)], unique=True)

    @staticmethod    
    async def add_ruleset(tenant_id: str, ruleset_request: AddRulesetRequest): 
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        # Create Ruleset Data from the request
        ruleset_data = Ruleset(
            tenant_id=tenant.tenant_id,
            ruleset_name=ruleset_request.ruleset_name,
            description=ruleset_request.description,
            conditions=ruleset_request.conditions,
            default_action=ruleset_request.default_action,
            global_access_policy=ruleset_request.global_access_policy,
            group_access_policy=ruleset_request.group_access_policy,
            user_specific_access_policy=ruleset_request.user_specific_access_policy
        )

        collection_schema = mongodb.db["rulesets"]

        try:
            result = await collection_schema.insert_one(ruleset_data.dict())
            return {"message": "Ruleset added successfully", "ruleset_id": str(result.inserted_id)}
        except DuplicateKeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Ruleset with the name '{ruleset_data.ruleset_name}' already exists for this tenant."
            )       

    @staticmethod
    async def get_ruleset(tenant_id: str, ruleset_name: str):
        # Call get_tenant to Check if tenant exists
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        collection = mongodb.db["rulesets"]
        ruleset = await collection.find_one({"tenant_id": tenant.tenant_id, "ruleset_name": ruleset_name})

        if not ruleset:
            raise HTTPException(
                status_code=404,
                detail=f"No Ruleset found with name '{ruleset_name}' for tenant '{tenant.tenant_id}'."
            )

        return RulesetResponse(**ruleset)

    @staticmethod
    async def update_ruleset(tenant_id: str, ruleset_name: str, update_ruleset_request: AddRulesetRequest):
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        collection_schema = mongodb.db["rulesets"]

        current_ruleset = await collection_schema.find_one({"tenant_id": tenant.tenant_id, "ruleset_name": ruleset_name})

        if not current_ruleset:
            raise HTTPException(
                status_code=404,
                detail=f"Ruleset with name '{ruleset_name}' not found for tenant '{tenant.tenant_id}'."
            )

        update_ruleset_data = update_ruleset_request.dict(exclude_unset=True)
        fields_to_update = {key: value for key, value in update_ruleset_data.items() if value is not None}

        try:
            if fields_to_update:
                update_result = await collection_schema.update_one(
                    {"tenant_id": tenant.tenant_id, "ruleset_name": ruleset_name},
                    {"$set": fields_to_update}
                )

                if update_result.matched_count == 0:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Ruleset with name '{ruleset_name}' not found for tenant '{tenant.tenant_id}'."
                    )

            updated_ruleset_data = await collection_schema.find_one({"tenant_id": tenant.tenant_id, "ruleset_name": ruleset_name})
            updated_ruleset = RulesetResponse(**updated_ruleset_data)

            return {
                "message": "Ruleset updated successfully",
                "updated_ruleset": updated_ruleset
            }

        except ValueError as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error updating ruleset: {str(e)}"
            )

    @staticmethod
    async def delete_ruleset(tenant_id: str, ruleset_name: str):
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        collection = mongodb.db["rulesets"]
        result = await collection.delete_one({"tenant_id": tenant.tenant_id, "ruleset_name": ruleset_name})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Ruleset not found"
            )

        return {"message": "Ruleset deleted successfully"}
