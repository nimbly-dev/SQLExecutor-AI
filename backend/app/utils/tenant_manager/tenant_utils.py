import bcrypt

from utils.database import mongodb
from fastapi import HTTPException

from model.authentication.admin_user import AdminUser
from utils.hash_utils import hash_password

class TenantUtils:

    @staticmethod
    async def initialize_default_admin_user(tenant_id: str):
        """
        Initialize default admin users for a tenant directly in MongoDB.
        """
        collection = mongodb.db["tenants"]
        tenant_data = await collection.find_one({"tenant_id": tenant_id})
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant not found")

        default_password = f"temp_password_{tenant_id}"
        default_admins = [
            AdminUser(user_id=f"{tenant_id}_admin", password=hash_password(default_password), role="Tenant Admin"),
            AdminUser(user_id=f"{tenant_id}_ruleset_admin", password=hash_password(default_password), role="Ruleset Admin"),
            AdminUser(user_id=f"{tenant_id}_schema_admin", password=hash_password(default_password), role="Schema Admin")
        ]

        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"admins": [admin.dict() for admin in default_admins]}},
            upsert=False
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize default admins for tenant"
            )

        return {"message": "Default admins initialized successfully"}

