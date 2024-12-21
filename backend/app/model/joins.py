from pydantic import BaseModel, root_validator
from typing import Optional, List
import re

VALID_JOIN_TYPES = {"INNER", "LEFT", "RIGHT", "OUTER"}

class Joins(BaseModel):
    description: Optional[str] = None
    exclude_description_on_generate_sql: bool 
    table: str  
    on: str  
    type: str 
    
    @root_validator(pre=True)
    def check_values(cls, values):
        # Validate 'type'
        join_type = values.get('type')
        if join_type and join_type not in VALID_JOIN_TYPES:
            raise ValueError(f"Invalid join type '{join_type}', allowed join types are: {', '.join(VALID_JOIN_TYPES)}")

        # Validate 'description' length
        description = values.get('description')
        if description and len(description) > 64:
            raise ValueError("Joins Description must not exceed 64 characters.")

        # Validate 'on' condition
        on_condition = values.get('on')
        if on_condition:
            on_pattern = r"^[\w_]+\.[\w_]+\s*=\s*[\w_]+\.[\w_]+$"
            if not re.match(on_pattern, on_condition):
                raise ValueError("Invalid 'on' condition format. Expected format is 'table.column = other_table.column'.")
        
        # Validate 'table' field: it should be a non-empty string
        table = values.get('table')
        if not table or not isinstance(table, str):
            raise ValueError(f"Invalid 'table' name: '{table}'. It must be a non-empty string.")

        return values