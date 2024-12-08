from pydantic import BaseModel, Field, root_validator
from typing import Dict

from model.table_rule import TableRule

class UserSpecificAccessPolicy(BaseModel):
    user_identifier: str 
    tables: Dict[str, TableRule]