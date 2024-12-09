from utils.database import mongodb
from typing import Dict
from fastapi import HTTPException
from pymongo import ASCENDING

from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from model.tenant import Tenant
from model.setting import Setting
from model.requests.tenant_manager.add_setting_to_tenant_request import AddSettingToTenantRequest

class TenantSettingsService:
        
    @staticmethod
    async def create_indexes():
        collection_schema = mongodb.db["tenants"]
        await collection_schema.create_index(
            [("tenant_id", ASCENDING), ("settings", ASCENDING)], 
            unique=True
        )
    
    @staticmethod
    async def add_settings_to_tenant(tenant_id: str, add_settings_request: AddSettingToTenantRequest):
        collection = mongodb.db["tenants"]

        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant with id {tenant_id} not found"
            )

        if tenant.settings is None:
            tenant.settings = {}

        conflicting_keys = []
        new_settings = add_settings_request.dict()  

        for category, setting in new_settings.items():
            if category in tenant.settings:
                conflicting_keys.append(category)
            else:
                tenant.settings[category] = setting.dict() if isinstance(setting, Setting) else setting

        if conflicting_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Setting keys already exist for this tenant: {', '.join(conflicting_keys)}"
            )

        # Convert all settings to plain dictionaries before updating the database
        plain_settings = {key: value if isinstance(value, dict) else value.dict() for key, value in tenant.settings.items()}

        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"settings": plain_settings}},
            upsert=False
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Failed to insert settings into tenant"
            )

        return {
            "message": "Settings inserted successfully into tenant",
            "new_settings": plain_settings
        }

        
    @staticmethod
    async def update_settings_to_tenant(tenant_id: str, update_settings_request: AddSettingToTenantRequest):
        collection = mongodb.db["tenants"]

        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        new_settings = {category: setting.dict() for category, setting in update_settings_request.__root__.items()}

        # Check if there are changes
        if tenant.settings == new_settings:
            return {"message": "No changes to settings were made."}

        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"settings": new_settings}},
            upsert=False
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update settings for tenant")

        return {
            "message": "Settings updated successfully for tenant",
            "updated_settings": new_settings
        }

    @staticmethod
    async def delete_setting(tenant_id: str, setting_key: str):
        collection = mongodb.db["tenants"]

        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        if not tenant or setting_key not in tenant.settings:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant '{tenant_id}' or setting key '{setting_key}' not found"
            )

        setting = tenant.settings[setting_key]
        if isinstance(setting, Setting):
            setting = setting.dict()

        if not setting.get("is_custom_setting", True):
            raise HTTPException(
                status_code=400,
                detail=f"Default setting '{setting_key}' cannot be deleted"
            )

        # Update settings and persist changes
        tenant.settings.pop(setting_key)
        updated_settings = {key: value.dict() if isinstance(value, Setting) else value for key, value in tenant.settings.items()}

        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"settings": updated_settings}},
            upsert=False
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete setting '{setting_key}' for tenant {tenant_id}"
            )

        return {
            "message": f"Setting '{setting_key}' successfully deleted for tenant {tenant_id}",
            "updated_settings": updated_settings
        }
        
    @staticmethod
    async def get_settings(tenant_id: str):
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant with id {tenant_id} not found"
            )
            
        return {
            "settings": tenant.settings or {}
        }

    @staticmethod
    async def get_setting_detail(tenant_id: str, setting_key: str):
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        if not tenant or setting_key not in tenant.settings:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant '{tenant_id}' or setting key '{setting_key}' not found"
            )

        setting_detail = tenant.settings[setting_key]
        if isinstance(setting_detail, Setting):
            setting_detail = setting_detail.dict()

        return {
            "setting_key": setting_key,
            "setting_detail": {
                "setting_basic_name": setting_detail.get("setting_basic_name", ""),
                "setting_value": setting_detail.get("setting_value", ""),
                "setting_category": setting_detail.get("setting_category", ""),
                "is_custom_setting": setting_detail.get("is_custom_setting", False),
            }
        }