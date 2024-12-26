from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from model.authentication.external_user_session_data_setting import ExternalSessionDataSetting

class ExternalSessionData(BaseModel):
    session_id: UUID = Field(..., description="A unique session identifier.")
    tenant_id: str = Field(..., description="The tenant identifier.")
    user_id: str = Field(..., description="The user identifier.")
    custom_fields: Dict[str, Any] = Field(..., description="Custom fields included in the session, e.g., roles or permissions.")
    created_at: datetime = Field(..., description="The UTC timestamp when the session was created.")
    expires_at: datetime = Field(..., description="The UTC timestamp when the session expires.")
    session_settings: Optional[Dict[str, Dict[str, ExternalSessionDataSetting]]] = Field(
        default_factory=dict, description="Session-specific settings overriding tenant settings."
    )
