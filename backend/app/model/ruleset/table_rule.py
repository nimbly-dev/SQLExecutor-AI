from pydantic import BaseModel, Field, root_validator
from typing import Dict, List, Union
import re

from model.ruleset.column_rule import ColumnRule

class TableRule(BaseModel):
    columns: ColumnRule
    condition: str

    @root_validator(pre=True)
    def validate_table_rule(cls, values):
        columns = values.get("columns")
        if not isinstance(columns, dict):
            raise ValueError("The 'columns' field must be a dictionary.")
        try:
            values["columns"] = ColumnRule(**columns)
        except Exception as e:
            raise ValueError(f"Error validating 'columns': {str(e)}")
        return values

    @staticmethod
    def is_valid_dynamic_condition(value: str) -> bool:
        """
        Validate if the condition contains supported placeholders or operators,
        and supports arrays, booleans, and single-digit numbers.

        Args:
            value (str): The condition string.

        Returns:
            bool: True if the condition is valid, False otherwise.
        """
        if value in {"TRUE", "FALSE"}:  # Allow direct booleans
            return True

        # Valid logical and comparison operators
        valid_operators = ["==", "AND", "OR", "IN", "NOT", "<", ">", "<=", ">="]
        if any(op in value for op in valid_operators):
            return True

        # Placeholder validation (e.g., "${jwt.user_id}")
        if re.search(r"\$\{jwt\.[a-zA-Z0-9_.]+\}", value):
            return True

        # Support arrays (e.g., "[1, 2, 3]" or "['admin', 'user']")
        try:
            eval_value = eval(value)
            if isinstance(eval_value, (list, int, float, bool)):
                return True
        except (SyntaxError, NameError):
            pass

        return False