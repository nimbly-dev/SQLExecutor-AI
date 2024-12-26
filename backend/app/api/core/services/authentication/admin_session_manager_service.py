

from datetime import datetime, timezone, timedelta
from utils.database import mongodb
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from datetime import datetime, timezone
from uuid import uuid4

from model.tenant.tenant import Tenant
from model.requests.authentication.auth_admin_login_request import AuthLoginRequest
from model.authentication.admin_session_data import AdminSessionData



class AdminSessionManagerService:
    
    @staticmethod
    async def initialize_ttl_index():
        """
        Ensure the TTL index is created on the 'expires_at' field of the 'sessions' collection.
        """
        collection =  mongodb.db["admin_sessions"]
        await collection.create_index(
            "expires_at",
            expireAfterSeconds=0 
        )
