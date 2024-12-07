from pydantic import BaseModel, Field, root_validator
from typing import Optional
from bson import ObjectId

class Tenant(BaseModel):
    tenant_id: str = Field(..., max_length=36)
    tenant_name: str = Field(..., description="Name of the tenant")
    _id: Optional[str]

    @root_validator(pre=True)
    def check_tenant_id_length(cls, values):
        tenant_id = values.get('tenant_id')
        if tenant_id and len(tenant_id) > 36:
            raise ValueError("tenant_id must be at most 36 characters")
        return values

    class Config:
        json_encoders = {
            ObjectId: str
        }