from pydantic import BaseModel
from typing import List, Optional, Dict
from bson import ObjectId

from model.ruleset.global_access_policy import GlobalAccessPolicy
from model.ruleset.group_access_policy import GroupAccessPolicy
from model.ruleset.user_specific_access_policy import UserSpecificAccessPolicy

class RulesetResponse(BaseModel):
    tenant_id: str
    ruleset_name: str
    description: str
    is_ruleset_enabled: bool
    conditions: Optional[Dict[str, str]] = None  
    global_access_policy: GlobalAccessPolicy
    group_access_policy: Optional[Dict[str, GroupAccessPolicy]]
    user_specific_access_policy: Optional[List[UserSpecificAccessPolicy]] = None

    class Config:
        json_encoders = {
            ObjectId: str,
            GlobalAccessPolicy: lambda v: v.dict(),
            GroupAccessPolicy: lambda v: v.dict(),
            UserSpecificAccessPolicy: lambda v: v.dict()
        }
