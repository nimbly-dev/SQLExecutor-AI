from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional, Dict, List
from model.table import Table

import re

class AddSchemaRequest(BaseModel):
    schema_name: str  
    description: str
    tables: Dict[str, Table]
    exclude_description_on_generate_sql: bool  
    filter_rules: Optional[List[str]] = [] 

    @validator('schema_name')
    def validate_schema_name(cls, v):
        if not isinstance(v, str):
            raise ValueError(f"Schema name must be a string, but got {type(v)}")
        
        v = v.strip()

        if '\n' in v or '\t' in v or ' ' in v:
            raise ValueError(f"Invalid schema name: '{v}'. It should not contain spaces, tabs, or newlines.")
        
        pattern = r"^[a-zA-Z0-9_]+$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid schema name: '{v}'. It should only contain letters, numbers, and underscores, with no spaces.")
        return v
    
    @root_validator(pre=True)
    def check_description_length(cls, values):
        description = values.get('description')
        if description and len(description) > 64:
            raise ValueError("description must not exceed 64 characters")
        return values
