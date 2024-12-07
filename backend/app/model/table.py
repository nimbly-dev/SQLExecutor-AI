from pydantic import BaseModel, root_validator
from typing import Dict, Optional, List
from model.column import Column
from model.joins import Joins

class Table(BaseModel):
    columns: Dict[str, Column]
    description: Optional[str] = None  
    synonyms: Optional[List[str]] = []  
    relationships: Optional[Dict[str, Joins]] = {}  

    @root_validator(pre=True)
    def check_description_length(cls, values):
        description = values.get('description')
        if description and len(description) > 64:
            raise ValueError("description must not exceed 64 characters")
        return values