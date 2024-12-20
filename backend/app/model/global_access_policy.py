from pydantic import BaseModel
from typing import Dict
from model.table_rule import TableRule

class GlobalAccessPolicy(BaseModel):
    tables: Dict[str, TableRule]
