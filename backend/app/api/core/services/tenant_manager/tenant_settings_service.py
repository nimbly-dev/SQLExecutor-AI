from utils.database import mongodb
from typing import Dict, List
from fastapi import HTTPException
from pymongo import ASCENDING

from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from model.tenant.tenant import Tenant
from model.tenant.setting import Setting
from model.requests.tenant_manager.add_setting_to_tenant_request import AddSettingToTenantRequest
from model.requests.tenant_manager.update_setting_to_tenant_request import UpdateSettingRequest
        
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
        """
        Add or append settings to a tenant.
        If a category does not exist, it will be created.
        If a category exists:
            - If the setting key already exists, throw a 400 error.
            - Otherwise, append the new setting.
        """
        collection = mongodb.db["tenants"]
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        def ensure_dict(obj):
            if isinstance(obj, Setting):
                return {
                    "setting_description": obj.setting_description,
                    "setting_basic_name": obj.setting_basic_name,
                    "setting_default_value": obj.setting_default_value,
                    "setting_value": obj.setting_value,
                    "is_custom_setting": obj.is_custom_setting
                }
            return obj

        # Clean any existing Setting objects in tenant.settings
        cleaned_settings = {
            cat: {
                key: ensure_dict(val)
                for key, val in cat_settings.items()
            } for cat, cat_settings in tenant.settings.items()
        }

        tenant.settings = cleaned_settings
        new_settings = add_settings_request.__root__


        for category, settings_dict in new_settings.items():
            if category not in tenant.settings:
                # Create category if it does not exist
                tenant.settings[category] = {
                    setting_key: {
                        "setting_description": setting_val.setting_description,
                        "setting_basic_name": setting_val.setting_basic_name,
                        "setting_default_value": setting_val.setting_default_value,
                        "setting_value": setting_val.setting_value,
                        "is_custom_setting": setting_val.is_custom_setting
                    }
                    for setting_key, setting_val in settings_dict.items()
                }
            else:
                # Category exists, verify no duplicates before adding
                existing_keys = tenant.settings[category].keys()
                duplicate_keys = [k for k in settings_dict.keys() if k in existing_keys]
                if duplicate_keys:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Setting keys already exist in category '{category}': {', '.join(duplicate_keys)}"
                    )

                # Append new settings
                for setting_key, setting_val in settings_dict.items():
                    tenant.settings[category][setting_key] = {
                        "setting_description": setting_val.setting_description,
                        "setting_basic_name": setting_val.setting_basic_name,
                        "setting_default_value": setting_val.setting_default_value,
                        "setting_value": setting_val.setting_value,
                        "is_custom_setting": setting_val.is_custom_setting
                    }

        # Update the tenant in the database
        update_doc = {"$set": {"settings": tenant.dict()["settings"]}}
        result = await collection.update_one({"tenant_id": tenant_id}, update_doc, upsert=False)

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Failed to insert or append settings into tenant"
            )

        return {
            "new_settings": tenant.settings
        }
        
    @staticmethod
    async def update_cat_settings_to_tenant(tenant_id: str, category_key: str, category_settings: UpdateSettingRequest):
        collection = mongodb.db["tenants"]
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        # Validate category key existence
        if category_key not in tenant.settings:
            raise HTTPException(
                status_code=404,
                detail=f"Category '{category_key}' not found in tenant settings"
            )

        update_query = {
            f"settings.{category_key}.{key}": val.to_dict()
            for key, val in category_settings.__root__.items()
        }
        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": update_query},
            upsert=False
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=400, detail="No matching tenant found.")

        updated_tenant = await collection.find_one({"tenant_id": tenant_id}, {"settings": 1})
        updated_settings = updated_tenant["settings"].get(category_key, {})

        if result.modified_count == 0:
            return {
                "message": f"Category '{category_key}' settings were already up-to-date.",
                "updated_settings": updated_settings
            }

        return {
            "message": f"Category '{category_key}' settings updated successfully.",
            "updated_settings": updated_settings
        }


    @staticmethod
    async def get_tenant_settings(tenant_id: str):
        """
        Get tenant settings or just categories based on the categories_only flag.
        
        Args:
            tenant_id (str): The ID of the tenant
            categories_only (bool, optional): If True, return only categories. Defaults to False.
        """ 
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        return {"settings": tenant.settings or {}}

    @staticmethod
    async def get_setting_detail(tenant_id: str, setting_category: str, setting_key: str):
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        # Search setting by key
        category_settings = tenant.settings[setting_category]
        if setting_key not in category_settings:
            raise HTTPException(
                status_code=404,
                detail=f"Setting '{setting_key}' not found in category '{setting_category}'"
            )

        setting_detail = category_settings[setting_key]

        return {
            "setting_key": setting_key,
            "setting_detail": setting_detail.dict()
        }

    @staticmethod
    async def get_setting_details_by_category(tenant_id: str, setting_category: str):
        """
        Get all settings for a specific category.
        
        Args:
            tenant_id (str): The ID of the tenant
            setting_category (str): The category to get settings for
            
        Returns:
            Dict containing the category settings
            
        Raises:
            HTTPException: If category is not found
        """
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        if setting_category not in tenant.settings:
            raise HTTPException(
                status_code=404,
                detail=f"Category '{setting_category}' not found in tenant settings"
            )

        category_settings = tenant.settings[setting_category]
        return {
            "category": setting_category,
            "settings": {
                key: setting.dict() if isinstance(setting, Setting) else setting
                for key, setting in category_settings.items()
            }
        }

    @staticmethod
    async def delete_setting(tenant_id: str, setting_category: str, setting_key: str):
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)

        # Delete setting by key
        category_settings = tenant.settings[setting_category]
        if setting_key not in category_settings:
            raise HTTPException(
                status_code=404,
                detail=f"Setting '{setting_key}' not found in category '{setting_category}'"
            )

        del category_settings[setting_key]

        # Update tenant settings in database
        collection = mongodb.db["tenants"]
        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {f"settings.{setting_category}": {key: val.to_dict() for key, val in category_settings.items()}}},
            upsert=False
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to delete setting for tenant")

        return {
            "message": f"Setting '{setting_key}' deleted successfully from category '{setting_category}'",
            "updated_settings": category_settings
        }

    @staticmethod
    async def get_tenant_setting_categories(tenant_id: str) -> Dict[str, List[str]]:
        """
        Get all categories and their setting keys from tenant settings.
        
        Args:
            tenant_id (str): The ID of the tenant
            
        Returns:
            Dict[str, List[str]]: Dictionary with categories as keys and lists of setting keys as values
        """
        tenant: Tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
        
        if not tenant.settings:
            return {"categories": []}
            
        categories_info = {
            "categories": list(tenant.settings.keys())
        }
        
        return categories_info
