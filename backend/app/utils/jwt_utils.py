import jwt
import logging

from pydantic import ValidationError
from fastapi import Depends, HTTPException, Header
from utils.database import mongodb
from uuid import UUID
from datetime import datetime, timezone
from model.setting import Setting
from model.tenant import Tenant
from model.session_data import SessionData

logger = logging.getLogger(__name__)

def decode_jwt(token: str, secret_key: str):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'
    
async def authenticate_session(x_session_id: str = Header(...)) -> SessionData:
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
        return SessionData(**session)
    except ValidationError as e:
        logger.error("Invalid session data: %s", e)
        raise HTTPException(status_code=500, detail="Invalid session data format")


async def validate_api_key(x_api_key: str = Header(...), tenant_id: str = None):
    """Validate API key against tenant settings."""
    tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": tenant_id})
    if not tenant_data:
        logger.warning("Tenant not found: %s", tenant_id)
        raise HTTPException(status_code=404, detail="Tenant not found")

    api_key_setting = (Tenant(**tenant_data).settings or {}).get("TENANT_APPLICATION_TOKEN")
    if not api_key_setting or x_api_key != api_key_setting.setting_value:
        logger.warning("Invalid API Key for tenant: %s", tenant_id)
        raise HTTPException(status_code=403, detail="Invalid API Key")
