from utils.database import mongodb
from fastapi import HTTPException
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from typing import Union, List, Dict, Any, Optional
from model.ruleset.ruleset import Ruleset
from model.tenant.tenant import Tenant
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest
from model.responses.ruleset_manager.ruleset_response import RulesetResponse

from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from utils.schema.schema_utils import schema_exists

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
            connected_schema_name=ruleset_request.connected_schema_name,
            description=ruleset_request.description,
            conditions=ruleset_request.conditions,
            is_ruleset_enabled=ruleset_request.is_ruleset_enabled,
            global_access_policy=ruleset_request.global_access_policy,
            group_access_policy=ruleset_request.group_access_policy,
            user_specific_access_policy=ruleset_request.user_specific_access_policy,
            injectors=ruleset_request.injectors
        )

        collection_schema = mongodb.db["rulesets"]


        if not await schema_exists(tenant_id=tenant.tenant_id, schema_name=ruleset_data.connected_schema_name):
            raise HTTPException(
            status_code=404,
            detail=f"Ruleset '{ruleset_data.connected_schema_name}' not found for tenant '{tenant.tenant_id}'."
            )

        try:
            await collection_schema.insert_one(ruleset_data.dict())
            return Ruleset(**ruleset_data.dict())
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
        ruleset = await collection.find_one({"tenant_id": tenant_id, "ruleset_name": ruleset_name})

        if not ruleset:
            raise HTTPException(
                status_code=404,
                detail=f"No Ruleset found with name '{ruleset_name}' for tenant '{tenant.tenant_id}'."
            )

        return RulesetResponse(**ruleset)
    
    @staticmethod
    async def get_rulesets_summary(tenant_id: str) -> List[Dict[str, Any]]:
        collection = mongodb.db["rulesets"]
        rulesets_cursor = collection.find(
            {"tenant_id": tenant_id}, 
            {"ruleset_name": 1, "description": 1, "is_ruleset_enabled": 1, 
             "connected_schema_name": 1, "injectors": 1, "_id": 0
            }
        )
        
        rulesets = []
        
        async for ruleset_data in rulesets_cursor:
            ruleset_info = {
                "ruleset_name": ruleset_data["ruleset_name"],
                "description": ruleset_data["description"],
                "connected_schema_name": ruleset_data["connected_schema_name"],
                "is_ruleset_enabled": ruleset_data["is_ruleset_enabled"],
                "has_injectors": bool(ruleset_data.get("injectors", {}))
            }
            
            rulesets.append(ruleset_info)
        
        return rulesets

    @staticmethod
    async def get_rulesets_summary_paginated(
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        filter_name: Optional[str] = None,
        is_ruleset_enabled: Optional[bool] = None,
        has_injectors: Optional[bool] = None
    ) -> Dict[str, Any]:
        collection = mongodb.db["rulesets"]
        skip = (page - 1) * page_size

        # Build query with tenant_id
        query: Dict[str, Any] = {"tenant_id": tenant_id}

        # Add name filter if provided
        if filter_name:
            # Split the filter string into keywords for a more precise match
            keywords = filter_name.split()
            # Each keyword must match either the ruleset_name or description
            query["$and"] = [
                {"$or": [
                    {"ruleset_name": {"$regex": keyword, "$options": "i"}},
                    {"description": {"$regex": keyword, "$options": "i"}}
                ]}
                for keyword in keywords
            ]

        # Add enabled filter if provided
        if is_ruleset_enabled is not None:
            query["is_ruleset_enabled"] = is_ruleset_enabled

        # Add injectors filter if provided
        if has_injectors is not None:
            if has_injectors:
                # If true, find documents where injectors exists and is not empty
                query["injectors"] = {"$exists": True, "$ne": {}}
            else:
                # If false, find documents where injectors doesn't exist or is empty
                query["$or"] = [
                    {"injectors": {"$exists": False}},
                    {"injectors": {}}
                ]

        rulesets_cursor = collection.find(
            query,
            {
                "ruleset_name": 1,
                "description": 1,
                "is_ruleset_enabled": 1,
                "connected_schema_name": 1,
                "injectors": 1,
                "_id": 0
            }
        ).skip(skip).limit(page_size)

        rulesets = []
        async for ruleset_data in rulesets_cursor:
            ruleset_info = {
                "ruleset_name": ruleset_data["ruleset_name"],
                "description": ruleset_data["description"],
                "connected_schema_name": ruleset_data["connected_schema_name"],
                "is_ruleset_enabled": ruleset_data["is_ruleset_enabled"],
                "has_injectors": bool(ruleset_data.get("injectors", {}))
            }
            rulesets.append(ruleset_info)

        # Get total count for pagination
        total = await collection.count_documents(query)

        if not rulesets:
            raise HTTPException(
                status_code=404,
                detail=f"No rulesets found for tenant '{tenant_id}'."
            )

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "rulesets": rulesets
        }
    
    @staticmethod
    async def get_rulesets(tenant_id: str) -> List[RulesetResponse]:
        collection = mongodb.db["rulesets"]
        rulesets_cursor = collection.find({"tenant_id": tenant_id})
        rulesets = []

        try:
            async for ruleset_data in rulesets_cursor:
                rulesets.append(RulesetResponse(**ruleset_data))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse ruleset data for tenant '{tenant_id}': {e}"
            )

        if not rulesets:
            raise HTTPException(
                status_code=404,
                detail=f"No rulesets found for tenant '{tenant_id}'."
            )

        return rulesets


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

        # Convert update_ruleset_request to a dict and filter out unset fields
        update_ruleset_data = update_ruleset_request.dict(exclude_unset=True)
        fields_to_update = {key: value for key, value in update_ruleset_data.items() if value is not None}
        
        # Use dictionary access for connected_schema_name
        connected_schema_name = update_ruleset_data.get("connected_schema_name")
        if connected_schema_name and not await schema_exists(tenant_id=tenant.tenant_id, schema_name=connected_schema_name):
            raise HTTPException(
                status_code=404,
                detail=f"Ruleset '{connected_schema_name}' not found for tenant '{tenant.tenant_id}'."
            )

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

            return updated_ruleset
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


