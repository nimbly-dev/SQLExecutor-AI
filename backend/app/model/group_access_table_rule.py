from pydantic import BaseModel, Field, root_validator
from typing import Dict, List, Union
import re

from model.group_access_column_rule import GroupAccessColumnRule

class GroupAccessTableRule(BaseModel):
    columns: GroupAccessColumnRule

    @root_validator(pre=True)
    def validate_table_rule(cls, values):
        columns = values.get("columns", {})
        if not columns:
            raise ValueError("Each table must define 'columns'.")
        return values