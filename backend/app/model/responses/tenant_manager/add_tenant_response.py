from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from model.tenant.setting import Setting
from model.authentication.admin_user import AdminUser


class AddTenantResponse(BaseModel):
    tenant_id: str = Field(..., max_length=36)
    tenant_name: str = Field(..., description="Name of the tenant")
    settings: Optional[Dict[str, Dict[str, Setting]]] = {} 
    admins: List[AdminUser] = Field(default=[], description="List of admin users tied to the tenant.")

    class Config:
        orm_mode = True
