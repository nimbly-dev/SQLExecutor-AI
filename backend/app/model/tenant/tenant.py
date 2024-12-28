from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List
from bson import ObjectId

from model.tenant.setting import Setting
from model.authentication.admin_user import AdminUser

import re

class Tenant(BaseModel):
    tenant_id: str = Field(..., max_length=36)
    tenant_name: str = Field(..., description="Name of the tenant")
    admins: List[AdminUser] = Field(default=[], description="List of admin users tied to the tenant.")
    settings: Optional[Dict[str, Dict[str, Setting]]] = {}
    _id: Optional[str]
    
    @root_validator(pre=True)
    def validate_tenant_id(cls, values):
        tenant_id = values.get('tenant_id')
        # Pre-process to uppercase
        tenant_id = tenant_id.upper()

        # Validate length
        if len(tenant_id) > 36:
            raise ValueError("tenant_id must be at most 36 characters")

        # Validate format: Only letters, numbers, and underscores, no spaces
        if not re.match(r'^[A-Z0-9_]*$', tenant_id):
            raise ValueError(
                "tenant_id can only contain uppercase letters, numbers, and underscores (_), and must not contain spaces"
            )
            
        # Save preprocessed tenant_id
        values['tenant_id'] = tenant_id
        return values
    class Config:
        json_encoders = {
            ObjectId: str
        }

