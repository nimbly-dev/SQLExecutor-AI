from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List
from bson import ObjectId

from model.global_access_policy import GlobalAccessPolicy
from model.table_access_policy import TableAccessPolicy
from model.user_specific_access_policy import UserSpecificAccessPolicy

class Ruleset(BaseModel):
    _id: Optional[str]
    tenant_id: str = Field(..., max_length=36)
    ruleset_name: str
    description: str
    default_action: str
    global_access_policy: GlobalAccessPolicy
    table_access_policy: TableAccessPolicy
    user_specific_access_policy: Optional[List[UserSpecificAccessPolicy]] = None
    
    @root_validator
    def validate_ruleset(cls, values):
        default_action = values.get("default_action")
        allowed_actions = {"ALLOW", "DENY"}
        if default_action.upper() not in allowed_actions:
            raise ValueError(f"default_action must be one of {allowed_actions}, got '{default_action}'.")
        values["default_action"] = default_action.upper()
        return values
    
    
    # def sanitize_keys(self):
    #     """
    #     Replace `.` in keys of user_specific_access_policy with `_` for MongoDB compatibility.
    #     """
    #     if self.user_specific_access_policy:
    #         sanitized_policy = {}
    #         for key, value in self.user_specific_access_policy.items():
    #             sanitized_key = key.replace(".", "_")
    #             sanitized_policy[sanitized_key] = value
    #         self.user_specific_access_policy = sanitized_policy

    # def restore_keys(self):
    #     """
    #     Restore sanitized keys by replacing `_` back with `.`.
    #     """
    #     if self.user_specific_access_policy:
    #         restored_policy = {}
    #         for key, value in self.user_specific_access_policy.items():
    #             original_key = key.replace("_", ".")
    #             restored_policy[original_key] = value
    #         self.user_specific_access_policy = restored_policy
    
    class Config:
        # Encode Access Policies to dictionary
        json_encoders = {
            ObjectId: str,
            GlobalAccessPolicy: lambda v: v.dict(),  
            TableAccessPolicy: lambda v: v.dict(),
            UserSpecificAccessPolicy: lambda v: v.dict()
        }
