import secrets

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



    @staticmethod
    async def initialize_tenant_tokens(tenant_id: str):
        """
        Initialize dynamic tokens for tenant settings (Admin Token and Application Token).
        """
        collection = mongodb.db["tenants"]
        tenant_data = await collection.find_one({"tenant_id": tenant_id})
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Generate unique tokens
        admin_auth_token = secrets.token_hex(32)  # 256-bit secure token
        application_token = secrets.token_hex(32)

        token_settings = {
            "ADMIN_AUTH": {
                "ADMIN_AUTH_TOKEN": {
                    "setting_basic_name": "Tenant SQLExecutor Admin Token",
                    "setting_value": admin_auth_token,
                    "is_custom_setting": False,
                    "setting_description": "Admin authentication token for SQLExecutor",
                    "setting_default_value": ""
                }
            },
            "EXTERNAL_JWT_AUTH": {
                "TENANT_APPLICATION_TOKEN": {
                    "setting_basic_name": "Tenant SQLExecutor Application Token",
                    "setting_value": application_token,
                    "is_custom_setting": False,
                    "setting_description": "Application authentication token for SQLExecutor",
                    "setting_default_value": ""
                }
            }
        }

        settings = tenant_data.get("settings", {})
        for category, tokens in token_settings.items():
            if category not in settings:
                settings[category] = {}
            settings[category].update(tokens)

        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"settings": settings}},
            upsert=False
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize tokens for tenant"
            )
