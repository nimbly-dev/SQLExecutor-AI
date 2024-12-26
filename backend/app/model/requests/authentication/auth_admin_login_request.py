from pydantic import BaseModel, Field, root_validator

class AuthLoginRequest(BaseModel):
    user_id: str = Field(..., description="The input user identifier.")
    password: str = Field(..., description="The input user password.")
    tenant_id: str= Field(..., description="Tenant ID where the user will be logged into")