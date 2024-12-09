import json

from utils.database import mongodb
from fastapi import HTTPException
from typing import Dict

from model.tenant import Tenant
from model.setting import Setting

_DEFAULT_SETTINGS_PATH = '/app/resources/settings/default_settings.json'

class SettingUtils:

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
        initialized_settings: Dict[str, Setting] = {
            key: Setting(**value) for key, value in default_settings.items()
        }

        # Update tenant's settings
        tenant.settings = {key: value.dict() for key, value in initialized_settings.items()}
        result = await collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": {"settings": tenant.settings}},
            upsert=False
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
