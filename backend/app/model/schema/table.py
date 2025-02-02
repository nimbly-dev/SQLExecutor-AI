from pydantic import BaseModel, root_validator
from typing import Dict, Optional, List
from model.schema.column import Column
from model.schema.joins import Joins

class Table(BaseModel):
    columns: Dict[str, Column]
    description: Optional[str] = None  
    synonyms: Optional[List[str]] = []  
    relationships: Optional[Dict[str, Joins]] = {} 
    exclude_description_on_generate_sql: bool 

    @root_validator(pre=True)
    def check_description_length(cls, values):
        description = values.get('description')
        if description and len(description) > 64:
            raise ValueError("description must not exceed 64 characters")
        return values