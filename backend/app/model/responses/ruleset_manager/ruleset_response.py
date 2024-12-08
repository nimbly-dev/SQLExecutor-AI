from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from model.global_access_policy import GlobalAccessPolicy
from model.table_access_policy import TableAccessPolicy
from model.user_specific_access_policy import UserSpecificAccessPolicy

class RulesetResponse(BaseModel):
    tenant_id: str
    ruleset_name: str
    description: str
    default_action: str
    global_access_policy: GlobalAccessPolicy
    table_access_policy: TableAccessPolicy
    user_specific_access_policy: Optional[List[UserSpecificAccessPolicy]] = None

    class Config:
        # Convert ObjectId to string if it's present
        json_encoders = {
            ObjectId: str,
        }