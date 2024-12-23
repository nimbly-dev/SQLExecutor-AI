from pydantic import BaseModel
from typing import Dict
from model.ruleset.table_rule import TableRule

class GlobalAccessPolicy(BaseModel):
    tables: Dict[str, TableRule]
