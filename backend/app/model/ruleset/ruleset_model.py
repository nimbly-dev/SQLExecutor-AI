from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List
from bson import ObjectId

from model.ruleset.global_access_policy import GlobalAccessPolicy
from model.ruleset.group_access_policy import GroupAccessPolicy
from model.ruleset.user_specific_access_policy import UserSpecificAccessPolicy

class Ruleset(BaseModel):
    _id: Optional[str]
    tenant_id: str = Field(..., max_length=36)
    ruleset_name: str
    description: str
    default_action: str
    conditions: Optional[Dict[str, str]] = None  
    global_access_policy: GlobalAccessPolicy
    group_access_policy: Optional[Dict[str, GroupAccessPolicy]] = None
    user_specific_access_policy: Optional[List[UserSpecificAccessPolicy]] = None

    @root_validator
    def validate_ruleset(cls, values):
        default_action = values.get("default_action")
        allowed_actions = {"ALLOW", "DENY"}
        if default_action.upper() not in allowed_actions:
            raise ValueError(f"default_action must be one of {allowed_actions}, got '{default_action}'.")
        values["default_action"] = default_action.upper()
        return values

    class Config:
        json_encoders = {
            ObjectId: str,
            GlobalAccessPolicy: lambda v: v.dict(),
            GroupAccessPolicy: lambda v: v.dict(),
            UserSpecificAccessPolicy: lambda v: v.dict()
        }
