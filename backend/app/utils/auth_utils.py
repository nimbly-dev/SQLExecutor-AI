import jwt
import logging
import hmac
import hashlib

from pydantic import ValidationError
from fastapi import Depends, HTTPException, Header
from utils.database import mongodb
from uuid import UUID
from datetime import datetime, timezone
from model.tenant.setting import Setting
from model.tenant.tenant import Tenant
from model.authentication.admin_session_data import AdminSessionData
from model.external_system_integration.external_user_session_data import ExternalSessionData
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import API_KEYS, ADMIN_AUTH

logger = logging.getLogger(__name__)

def decode_jwt(token: str, secret_key: str):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'
    
async def authenticate_session(x_session_id: str = Header(...)) -> ExternalSessionData:
    """Authenticate session by validating session ID and expiration."""
    try:
        session_uuid = UUID(x_session_id)
    except ValueError:
        logger.warning("Invalid session ID format: %s", x_session_id)
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Retrieve session from MongoDB
    session = await mongodb.db["sessions"].find_one({"session_id": session_uuid})
    if not session:
        logger.warning("Session not found: %s", session_uuid)
        raise HTTPException(status_code=401, detail="Session not found or expired")

    expires_at = session["expires_at"].replace(tzinfo=timezone.utc) if session["expires_at"].tzinfo is None else session["expires_at"]
    if datetime.now(timezone.utc) > expires_at:
        logger.warning("Session expired: %s", session_uuid)
        raise HTTPException(status_code=401, detail="Session has expired")

    try:
        return ExternalSessionData(**session)
    except ValidationError as e:
        logger.error("Invalid session data: %s", e)
        raise HTTPException(status_code=500, detail="Invalid session data format")

async def authenticate_admin_session(authorization: str = Header(...)) -> AdminSessionData:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        tenant_id = unverified_payload.get("tenant_id")

        tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": tenant_id})
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant = Tenant(**tenant_data)
        ADMIN_AUTH_KEY = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=ADMIN_AUTH,
            setting_key="ADMIN_AUTH_TOKEN"
        )
        payload = jwt.decode(token, ADMIN_AUTH_KEY, algorithms=['HS256'])
        session_uuid = UUID(payload["session_id"])

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, ValueError) as e:
        logger.warning("Token validation failed: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    session = await mongodb.db["admin_sessions"].find_one({"session_id": session_uuid})
    if not session:
        logger.warning("Session not found or expired")
        raise HTTPException(status_code=401, detail="Session not found or expired")

    try:
        return AdminSessionData(**session)
    except ValidationError as e:
        logger.error("Invalid session data format: %s", str(e))
        raise HTTPException(status_code=500, detail="Invalid session data format")


async def validate_api_key(x_api_key: str = Header(...), tenant_id: str = None):
    """Validate API key against tenant settings."""
    tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": tenant_id})
    if not tenant_data:
        logger.warning("Tenant not found: %s", tenant_id)
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant = Tenant(**tenant_data)
    api_key_setting = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=API_KEYS,
        setting_key="TENANT_APPLICATION_TOKEN"
    )

    if not api_key_setting or x_api_key != api_key_setting:
        logger.warning("Invalid API Key for tenant: %s", tenant_id)
        raise HTTPException(status_code=403, detail="Invalid API Key")

async def validate_client_request(x_api_key: str = Header(...), tenant_id: str = None):
    """Validate client request using HMAC and tenant settings."""
    tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": tenant_id})
    
    
    if not tenant_data:
        logger.warning("Tenant not found: %s", tenant_id)
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant = Tenant(**tenant_data)
    encryption_key = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key="DEV_SQL_CONTEXT",
        setting_key="DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTION_KEY"
    )
    encryption_iv = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key="DEV_SQL_CONTEXT",
        setting_key="DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTION_IV"
    )
    encrypted_secret = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key="DEV_SQL_CONTEXT",
        setting_key="DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTED_SECRET"
    )

    if not encryption_key or not encryption_iv or not encrypted_secret:
        logger.warning("Missing encryption settings for tenant: %s", tenant_id)
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Create HMAC using the encryption key and IV
    hmac_key = encryption_key.encode()
    hmac_iv = encryption_iv.encode()
    hmac_secret = encrypted_secret.encode()

    # Generate HMAC digest
    hmac_digest = hmac.new(hmac_key, hmac_iv, hashlib.sha256).digest()

    # Compare the provided API key with the HMAC digest
    if not hmac.compare_digest(hmac_secret, hmac_digest):
        logger.warning("Invalid API Key for tenant: %s", tenant_id)
        raise HTTPException(status_code=403, detail="Invalid API Key")
