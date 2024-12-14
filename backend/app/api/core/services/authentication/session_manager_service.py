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
    async def create_jwt_session(decoded_jwt_token: DecodedJwtToken) -> SessionData:
        """
        Create a new session in the sessions collection based on the decoded JWT token.
        """
        collection = mongodb.db["sessions"]

        # Parse the expiration timestamp and convert to UTC
        expiration_datetime = datetime.fromisoformat(decoded_jwt_token.expiration)
        if expiration_datetime.tzinfo is not None:
            expiration_datetime = expiration_datetime.astimezone(timezone.utc)
        else:
            expiration_datetime = expiration_datetime.replace(tzinfo=timezone.utc)

        session_data = SessionData(
            session_id=uuid4(),
            tenant_id=decoded_jwt_token.tenant_id,
            user_id=decoded_jwt_token.user_identifier,
            custom_fields=decoded_jwt_token.custom_fields,
            created_at=datetime.now(timezone.utc),
            expires_at=expiration_datetime
        )

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