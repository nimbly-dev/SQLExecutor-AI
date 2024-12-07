from pydantic import BaseModel, root_validator
from typing import Optional, List

VALID_TYPES = {"INTEGER", "TEXT", "DECIMAL", "BOOLEAN", "DATE"}
VALID_CONSTRAINTS = {"PRIMARY KEY", "NOT NULL", "UNIQUE", "FOREIGN KEY"}

class Column(BaseModel):
    type: str 
    description: Optional[str] = None  
    constraints: Optional[List[str]] = []  
    synonyms: Optional[List[str]] = []  
    
    @root_validator(pre=True)
    def check_values(cls, values):
        # Validate 'type'
        column_type = values.get('type')
        if column_type and column_type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{column_type}', allowed types are: {', '.join(VALID_TYPES)}")

        # Validate 'constraints'
        constraints = values.get('constraints', [])
        for constraint in constraints:
            if constraint not in VALID_CONSTRAINTS:
                raise ValueError(f"Invalid constraint '{constraint}', allowed constraints are: {', '.join(VALID_CONSTRAINTS)}")
        
        # Validate 'description' length
        description = values.get('description')
        if description and len(description) > 64:
            raise ValueError("Description must not exceed 64 characters.")
        
        return values