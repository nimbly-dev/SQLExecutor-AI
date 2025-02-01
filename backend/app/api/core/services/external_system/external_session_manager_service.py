import pymongo

from utils.database import mongodb
from uuid import UUID
from typing import Any, Dict
from fastapi import HTTPException
from pymongo import ASCENDING
from pymongo.errors import PyMongoError
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase

from model.exceptions.base_exception_message import BaseExceptionMessage
from model.authentication.external_user_decoded_jwt_token import DecodedJwtToken
from model.external_system_integration.external_user_session_data import ExternalSessionData
from model.tenant.tenant import Tenant
from model.external_system_integration.external_user_session_data_setting import ExternalSessionDataSetting
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import(
    POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, SESSION_MANAGER_CATEGORY_KEY
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
    
    async def create_external_session(
        tenant: Tenant, 
        context_user_identifier: str, 
        custom_fields: Dict[str, Any]
    ) -> ExternalSessionData:
        collection = mongodb.db["sessions"]
        SESSION_EXPIRATION_TIME = SettingUtils.get_setting_value(
            tenant.settings,
            SESSION_MANAGER_CATEGORY_KEY,
            "SESSION_EXPIRATION_TIME"
        )

        if SESSION_EXPIRATION_TIME is None:
            raise ValueError("SESSION_EXPIRATION_TIME setting is not configured")

        expiration_datetime = datetime.now(timezone.utc) + timedelta(seconds=int(SESSION_EXPIRATION_TIME))
        
        # Populate session settings dynamically
        session_settings = SessionManagerService._populate_session_settings_from_tenant(tenant)
        
        session_data = ExternalSessionData(
            session_id=uuid4(),
            tenant_id=tenant.tenant_id,
            user_id=context_user_identifier,
            custom_fields=custom_fields,
            created_at=datetime.now(timezone.utc),
            expires_at=expiration_datetime,
            session_settings=session_settings  
        )
        
        try:
            await collection.insert_one(session_data.dict())
        except pymongo.errors.PyMongoError as e:
            raise ValueError(f"Failed to create session: {str(e)}")
        
        return session_data


    @staticmethod
    async def get_external_session(session_id: str):
        """
        Retrieve external session from DocumentDB
        """
        collection = mongodb.db["sessions"]

        try:
            try:
                session_uuid = UUID(session_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session_id format")
            
            session_data = await collection.find_one({"session_id": session_uuid})
            if session_data is None:
                return None
            
            if session_data:
                return ExternalSessionData(**session_data)
            return None
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

    @staticmethod
    async def delete_external_session(session_id: str) -> bool:
        """
        Logout Session by deleting external session on DocumentDB
        """
        collection = mongodb.db["sessions"]

        try:
            try:
                session_uuid = UUID(session_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session_id format")
            
            result = await collection.delete_one({"session_id": session_uuid})
            if result.deleted_count == 0:
                return False;
            
            return {"message": "Successfully logged out"}
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
        
    @staticmethod
    async def toggle_external_session_data(session_id: str, toggle: bool, setting_category: str, setting_name: str):
        """
        Toggle the session data in the 'sessions' collection.
        """
        collection = mongodb.db["sessions"]

        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=BaseExceptionMessage("Session ID is invalid"))
        
        try:
            session_data = await collection.find_one({"session_id": session_uuid})
            if session_data is None:
                raise HTTPException(status_code=400, detail=BaseExceptionMessage("Session not found"))
            
            session_data["session_settings"][setting_category][setting_name]["setting_value"] = str(toggle)
            result = await collection.update_one(
                {"session_id": session_uuid},
                {"$set": {"session_settings": session_data["session_settings"]}}
            )
            
            if result.modified_count == 0:
                return False
            
            return True
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")
        
        
    @staticmethod
    async def create_jwt_session(decoded_jwt_token: DecodedJwtToken, tenant: Tenant) -> ExternalSessionData:
        collection = mongodb.db["sessions"]
        expiration_datetime = datetime.fromisoformat(decoded_jwt_token.expiration)
        expiration_datetime = expiration_datetime.astimezone(timezone.utc) if expiration_datetime.tzinfo else expiration_datetime.replace(tzinfo=timezone.utc)

        session_settings = SessionManagerService._populate_session_settings_from_tenant(tenant)

        session_data = ExternalSessionData(
            session_id=uuid4(),
            tenant_id=decoded_jwt_token.tenant_id,
            user_id=decoded_jwt_token.user_identifier,
            custom_fields=decoded_jwt_token.custom_fields,
            created_at=datetime.now(timezone.utc),
            expires_at=expiration_datetime,
            session_settings=session_settings
        )

        try:
            await collection.insert_one(session_data.dict())
        except pymongo.errors.PyMongoError as e:
            raise ValueError(f"Failed to create session: {str(e)}")

        return session_data

    @staticmethod
    async def delete_jwt_session(session_id: str) -> bool:
        collection = mongodb.db["sessions"]

        try:
            session_uuid = UUID(session_id)
            result = await collection.delete_one({"session_id": session_uuid})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Session not found")
            return {"message": "Successfully logged out"}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session_id format")
        except pymongo.errors.PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
        
    @staticmethod
    def _populate_session_settings_from_tenant(tenant: Tenant) -> Dict[str, Dict[str, ExternalSessionDataSetting]]:
        """
        Internal method to populate session settings with specific keys only.
        """
        # Retrieve tenant settings
        tenant_settings = tenant.settings or {}

        # Populate only the required keys
        session_settings = {
            "SQL_GENERATION": {
                "REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": ExternalSessionDataSetting(
                    setting_basic_name="Remove Missing Columns on query scope",
                    setting_value=SettingUtils.get_setting_value(
                        tenant_settings,
                        POST_PROCESS_QUERYSCOPE_CATEGORY_KEY,
                        "TENANT_SETTING_REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE"
                    ) or "true",
                    setting_description="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE description not provided"
                )
            }
        }

        return session_settings