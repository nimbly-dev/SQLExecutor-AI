import json

from utils.database import mongodb
from fastapi import HTTPException
from typing import Dict

from model.tenant.tenant import Tenant
from model.tenant.setting import Setting

_DEFAULT_SETTINGS_PATH = '/app/resources/settings/default_settings.json'

class SettingUtils:

    @staticmethod
    def get_setting_value(settings, category_key, setting_key):
        category_settings = settings.get(category_key, {})
        setting = category_settings.get(setting_key)
        value = setting.setting_value if setting else None

        # Convert string 'True'/'False' to boolean
        if isinstance(value, str) and value.lower() in ["true", "false"]:
            return value.lower() == "true"

        return value


    @staticmethod
    async def initialize_default_tenant_settings(tenant_id: str):
        collection = mongodb.db["tenants"]
        tenant_data = await collection.find_one({"tenant_id": tenant_id})
        if not tenant_data:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )

        tenant = Tenant(**tenant_data)
        default_settings = SettingUtils.load_default_settings_json()

        # Check if settings are already initialized
        if tenant.settings:
            return {"message": "Tenant already has settings initialized"}

        # Initialize settings in the correct format
        initialized_settings = {
            category: {
                setting_name: Setting(
                    setting_description=setting_data.get("setting_description", ""),
                    setting_basic_name=setting_data["setting_basic_name"],
                    setting_default_value=setting_data.get("setting_default_value", ""),
                    setting_value=setting_data["setting_value"],
                    is_custom_setting=setting_data.get("is_custom_setting", False),
                ).dict()
                for setting_name, setting_data in settings.items()
            }
            for category, settings in default_settings.items()
        }

        # Update tenant's settings
        tenant.settings = initialized_settings
        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"settings": tenant.settings}},
            upsert=True
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Failed to initialize default settings for tenant"
            )

        return {"settings": tenant.settings}

    @staticmethod
    def load_default_settings_json() -> dict:
        try:
            with open(_DEFAULT_SETTINGS_PATH, 'r') as file:
                return json.load(file).get("settings", {})
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {_DEFAULT_SETTINGS_PATH}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON file: {_DEFAULT_SETTINGS_PATH}, error: {str(e)}")
