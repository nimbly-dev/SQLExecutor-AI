from pydantic import BaseModel, Field, root_validator
from typing import Dict, List

from model.table_rule import TableRule

class GlobalAccessPolicy(BaseModel):
    tables: Dict[str, TableRule]