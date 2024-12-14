from pydantic import BaseModel, Field
from typing import Dict, Any


class DecodedJwtToken(BaseModel):
    tenant_id: str
    custom_fields: Dict[str, Any] = Field(..., description="The dynamic custom fields included on JWT, e.g., roles or type.")
    user_identifier: str = Field(..., description="The user identifier field, e.g., sub, username, email.")
    expiration: str = Field(..., description="The expiration timestamp as an ISO 8601 string.")
