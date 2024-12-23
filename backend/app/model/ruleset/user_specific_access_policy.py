from pydantic import BaseModel, Field, root_validator
from typing import Dict

from model.ruleset.column_rule import ColumnRule
from model.ruleset.user_specific_table_rule import UserSpecificTableRule

class UserSpecificAccessPolicy(BaseModel):
    user_identifier: str
    tables: Dict[str, UserSpecificTableRule]