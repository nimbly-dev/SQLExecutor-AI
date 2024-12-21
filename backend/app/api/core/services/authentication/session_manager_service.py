import pymongo

from utils.database import mongodb
from uuid import UUID
from typing import Dict
from fastapi import HTTPException
from pymongo import ASCENDING
from pymongo.errors import PyMongoError
from datetime import datetime, timezone
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase

from model.decoded_jwt_token import DecodedJwtToken
from model.session_data import SessionData
from model.tenant import Tenant
from model.session_data_setting import SessionDataSetting
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import(
    POST_PROCESS_QUERYSCOPE_CATEGORY_KEY
)

class SessionManagerService:

    @staticmethod
    async def initialize_ttl_index():
        """
        Ensure the TTL index is created on the 'expires_at' field of the 'sessions' collection.
        """
        collection =  mongodb.db["sessions"]
        await collection.create_index(
            "expires_at",
            expireAfterSeconds=0 
        )

    @staticmethod
    async def create_jwt_session(decoded_jwt_token: DecodedJwtToken, tenant: Tenant) -> SessionData:
        """
        Create a new session in the sessions collection with dynamically populated settings.
        """
        collection = mongodb.db["sessions"]

        # Parse expiration timestamp
        expiration_datetime = datetime.fromisoformat(decoded_jwt_token.expiration)
        expiration_datetime = expiration_datetime.astimezone(timezone.utc) if expiration_datetime.tzinfo else expiration_datetime.replace(tzinfo=timezone.utc)

        # Populate session settings dynamically
        session_settings = SessionManagerService._populate_session_settings_from_tenant(tenant)

        # Create session data
        session_data = SessionData(
            session_id=uuid4(),
            tenant_id=decoded_jwt_token.tenant_id,
            user_id=decoded_jwt_token.user_identifier,
            custom_fields=decoded_jwt_token.custom_fields,
            created_at=datetime.now(timezone.utc),
            expires_at=expiration_datetime,
            session_settings=session_settings  # Attach settings directly
        )

        # Insert session into DB
        try:
            await collection.insert_one(session_data.dict())
        except pymongo.errors.PyMongoError as e:
            raise ValueError(f"Failed to create session: {str(e)}")

        return session_data


    @staticmethod
    async def delete_jwt_session(session_id: str) -> bool:
        """
        Logout Session by deleting JWT session on DocumentDB
        """
        collection = mongodb.db["sessions"]

        try:
            try:
                session_uuid = UUID(session_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session_id format")
            
            result = await collection.delete_one({"session_id": session_uuid})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return {"message": "Successfully logged out"}
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
        
        
    @staticmethod
    def _populate_session_settings_from_tenant(tenant: Tenant) -> Dict[str, Dict[str, SessionDataSetting]]:
        """
        Internal method to populate session settings with specific keys only.
        """
        # Retrieve tenant settings
        tenant_settings = tenant.settings or {}

        # Populate only the required keys
        session_settings = {
            "SQL_GENERATION": {
                "REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": SessionDataSetting(
                    setting_basic_name="Remove Missing Columns on query scope",
                    setting_value=SettingUtils.get_setting_value(
                        tenant_settings,
                        POST_PROCESS_QUERYSCOPE_CATEGORY_KEY,
                        "TENANT_SETTING_REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE"
                    ) or "true",
                    setting_description="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE description not provided"
                ),
                "IGNORE_COLUMN_WILDCARDS": SessionDataSetting(
                    setting_basic_name="Ignore Column Wildcards",
                    setting_value=SettingUtils.get_setting_value(
                        tenant_settings,
                        POST_PROCESS_QUERYSCOPE_CATEGORY_KEY,
                        "TENANT_SETTING_IGNORE_COLUMN_WILDCARDS"
                    ) or "true",
                    setting_description="IGNORE_COLUMN_WILDCARDS description not provided"
                )
            }
        }

        return session_settings