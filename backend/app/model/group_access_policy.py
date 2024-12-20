from pydantic import BaseModel, root_validator, Field
from typing import Dict
from model.group_access_table_rule import GroupAccessTableRule
from model.criteria import Criteria

class GroupAccessPolicy(BaseModel):
    description: str
    criteria: Criteria = Field(..., description="Criteria for applying this group policy.")
    tables: Dict[str, GroupAccessTableRule]