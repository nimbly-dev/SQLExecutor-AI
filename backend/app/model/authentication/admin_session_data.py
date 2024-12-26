from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class AdminSessionData(BaseModel):
    session_id: UUID = Field(..., description="A unique session identifier.")
    tenant_id: str = Field(..., description="The tenant identifier.")
    user_id: str = Field(..., description="The user identifier.")
    created_at: datetime = Field(..., description="Session creation timestamp in UTC.")
    expires_at: datetime = Field(..., description="Session expiration timestamp in UTC.")
    role: str = Field(..., description="Role of the Admin")