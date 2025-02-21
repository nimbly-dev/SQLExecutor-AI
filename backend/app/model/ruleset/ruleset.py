from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List
from bson import ObjectId

from model.ruleset.global_access_policy import GlobalAccessPolicy
from model.ruleset.group_access_policy import GroupAccessPolicy
from model.ruleset.user_specific_access_policy import UserSpecificAccessPolicy
from model.ruleset.injector import Injector

class Ruleset(BaseModel):
    _id: Optional[str]
    tenant_id: str = Field(..., max_length=36)
    ruleset_name: str
    connected_schema_name: str
    description: str
    is_ruleset_enabled: bool
    conditions: Optional[Dict[str, str]] = None  
    global_access_policy: GlobalAccessPolicy
    group_access_policy: Optional[Dict[str, GroupAccessPolicy]] = None
    user_specific_access_policy: Optional[List[UserSpecificAccessPolicy]] = None
    injectors: Optional[Dict[str, Injector]] = None 

    class Config:
        json_encoders = {
            ObjectId: str,
            GlobalAccessPolicy: lambda v: v.dict(),
            GroupAccessPolicy: lambda v: v.dict(),
            UserSpecificAccessPolicy: lambda v: v.dict()
        }
