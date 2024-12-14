from pydantic import BaseModel, Field
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

class SessionData(BaseModel):
    session_id: UUID = Field(..., description="A unique session identifier.")
    tenant_id: str = Field(..., description="The tenant identifier.")
    user_id: str = Field(..., description="The user identifier.")
    custom_fields: Dict[str, Any] = Field(..., description="Custom fields included in the session, e.g., roles or permissions.")
    created_at: datetime = Field(..., description="The UTC timestamp when the session was created.")
    expires_at: datetime = Field(..., description="The UTC timestamp when the session expires.")
