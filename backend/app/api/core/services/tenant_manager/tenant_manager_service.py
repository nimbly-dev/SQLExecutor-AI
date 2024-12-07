from utils.database import mongodb
from fastapi import HTTPException
from model.tenant import Tenant
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel

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
            
        await collection.insert_one(tenant.dict())
        return {"message": "Tenant created successfully"}

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
        collection = mongodb.db["tenants"]
        result = await collection.delete_one({"tenant_id": tenant_id})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )
            
        return {"message": "Tenant deleted successfully"}

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