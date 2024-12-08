from pydantic import BaseModel, Field, root_validator
from typing import Dict

from model.table_rule import TableRule

class TableAccessPolicy(BaseModel):
    tables: Dict[str, TableRule]