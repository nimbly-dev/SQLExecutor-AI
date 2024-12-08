from pydantic import BaseModel, Field, root_validator
from typing import Dict, List

from model.column_rule import ColumnRule

class TableRule(BaseModel):
    columns: ColumnRule
    condition: str

    @root_validator
    def validate_table_rule(cls, values):
        condition = values.get("condition")
        if not cls.is_valid_dynamic_condition(condition):
            raise ValueError(f"Invalid condition: {condition}")
        return values

    @staticmethod
    def is_valid_dynamic_condition(value: str) -> bool:
        if value in {"TRUE", "FALSE"}:
            return True
        return any(op in value for op in ["=", "AND", "OR", "${jwt."])