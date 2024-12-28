from pydantic import BaseModel, Field

class UpdateTenantRequestModel(BaseModel):
    tenant_name: str = Field(..., description="Name of the tenant")
    
    class Config:
        anystr_strip_whitespace = True 