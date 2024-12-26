import jwt

from datetime import datetime, timezone, timedelta
from utils.database import mongodb
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict

from model.tenant.tenant import Tenant
from model.requests.authentication.auth_admin_login_request import AuthLoginRequest
from model.authentication.admin_session_data import AdminSessionData
from utils.tenant_manager.setting_utils import SettingUtils

from api.core.constants.tenant.settings_categories import ADMIN_AUTH

class AdminAuthenticationService:
    
    # 24 Hrs Lifetime 1440
    # 4 days 5760
    SESSION_EXPIRY_MINUTES = 5760

    @staticmethod
    async def login_admin(auth_request: AuthLoginRequest) -> Dict:
        """
        Authenticate admin credentials and create a session.
        """
        # Fetch tenant
        tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": auth_request.tenant_id})
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant = Tenant(**tenant_data)

        # Find admin in tenant
        admin_user = next((admin for admin in tenant.admins if admin.user_id == auth_request.user_id), None)
        if not admin_user or not admin_user.verify_password(auth_request.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create session data
        session_data = AdminSessionData(
            session_id=uuid4(),
            tenant_id=tenant.tenant_id,
            user_id=admin_user.user_id,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=AdminAuthenticationService.SESSION_EXPIRY_MINUTES),
            role=admin_user.role
        )

        # Save session
        collection = mongodb.db["admin_sessions"]
        try:
            await collection.insert_one(session_data.dict())
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

        # Generate JWT token
        payload = {
            "session_id": str(session_data.session_id),
            "tenant_id": session_data.tenant_id,
            "user_id": session_data.user_id,
            "role": session_data.role,
            "exp": session_data.expires_at.timestamp()
        }
        ADMIN_AUTH_KEY = SettingUtils.get_setting_value(
                settings=tenant.settings,
                category_key=ADMIN_AUTH,
                setting_key="ADMIN_AUTH_TOKEN"
        )
        token = jwt.encode(payload, ADMIN_AUTH_KEY, algorithm='HS256')

        return {
            "JWT_TOKEN": f"Bearer {token}"
        }