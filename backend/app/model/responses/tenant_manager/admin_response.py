from pydantic import BaseModel, Field
from uuid import UUID

class GetAdminUserResponse(BaseModel):
    user_id: str = Field(..., description="The user identifier.")
    role: str = Field(..., description="Role of the Admin")
