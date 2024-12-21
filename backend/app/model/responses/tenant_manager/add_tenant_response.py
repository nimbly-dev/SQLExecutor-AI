from pydantic import BaseModel, Field
from typing import Optional, Dict
from model.setting import Setting


class AddTenantResponse(BaseModel):
    tenant_id: str = Field(..., max_length=36)
    tenant_name: str = Field(..., description="Name of the tenant")
    settings: Optional[Dict[str, Dict[str, Setting]]] = {} 

    class Config:
        orm_mode = True
