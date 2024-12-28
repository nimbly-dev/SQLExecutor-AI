from utils.database import mongodb
from fastapi import HTTPException
from typing import List

from model.tenant.tenant import Tenant
from model.schema.schema import Schema
from model.ruleset.ruleset import Ruleset
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel
from model.responses.tenant_manager.add_tenant_response import AddTenantResponse
from utils.tenant_manager.setting_utils import SettingUtils
from utils.tenant_manager.tenant_utils import TenantUtils

class TenantManagerService:
    
    @staticmethod
    async def add_tenant(tenant):
        collection = mongodb.db["tenants"]
        existing = await collection.find_one({"tenant_id": tenant.tenant_id})
        if existing:
            raise HTTPException(
                status_code=400,
                detail="A tenant with this tenant_id already exists"
            )

        try:
            await collection.insert_one(tenant.dict())
            await SettingUtils.initialize_default_tenant_settings(tenant_id=tenant.tenant_id)
            await TenantUtils.initialize_default_admin_user(tenant_id=tenant.tenant_id)
            await TenantUtils.initialize_tenant_tokens(tenant_id=tenant.tenant_id)
            
            tenant_data = await collection.find_one({"tenant_id": tenant.tenant_id})
            
            return {
                "message": "Tenant created successfully",
                "tenant": AddTenantResponse(**tenant_data)
            }
        except Exception as e:
            await collection.delete_one({"tenant_id": tenant.tenant_id})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize tenant. Rolled back changes. Error: {str(e)}"
            )

    @staticmethod
    async def get_tenant(tenant_id: str):
        collection = mongodb.db["tenants"]
        tenant = await collection.find_one({"tenant_id": tenant_id})
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )
        
        return Tenant(**tenant)
    
    @staticmethod
    async def delete_tenant(tenant_id: str):
        """
        Delete a tenant and remove all orphaned schemas and rulesets associated with it.

        Args:
            tenant_id (str): The ID of the tenant to be deleted.

        Returns:
            dict: Success message upon deletion.
        """
        tenants_collection = mongodb.db["tenants"]
        schemas_collection = mongodb.db["schemas"]
        rulesets_collection = mongodb.db["rulesets"]


        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        schema_delete_result = await schemas_collection.delete_many({"tenant_id": tenant_id})
        ruleset_delete_result = await rulesets_collection.delete_many({"tenant_id": tenant_id})


        tenant_delete_result = await tenants_collection.delete_one({"tenant_id": tenant_id})
        if tenant_delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return {
            "message": "Tenant and associated orphan data deleted successfully",
            "schemas_deleted": schema_delete_result.deleted_count,
            "rulesets_deleted": ruleset_delete_result.deleted_count
        }

    @staticmethod
    async def update_tenant(tenant_id: str, tenant_data: UpdateTenantRequestModel):
        tenant_data_dict = tenant_data.dict(exclude_unset=True)

        collection = mongodb.db["tenants"]
        result = await collection.update_one(
            {"tenant_id": tenant_id}, 
            {"$set": tenant_data_dict}  
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )

        return {"message": "Tenant updated successfully"}