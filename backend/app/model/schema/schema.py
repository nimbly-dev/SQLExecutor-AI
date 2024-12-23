from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List
from bson import ObjectId
from model.schema.table import Table, Column 

class Schema(BaseModel):
    tenant_id: str = Field(..., max_length=36)
    _id: Optional[str]
    schema_name: str
    description: str
    exclude_description_on_generate_sql: bool
    tables: Dict[str, Table]
    filter_rules: Optional[List[str]] = []

    @root_validator(pre=True)
    def check_description_length(cls, values):
        description = values.get('description')
        if description and len(description) > 64:
            raise ValueError("description must not exceed 64 characters")
        return values

    class Config:
        # Encode table and column to dictionary
        json_encoders = {
            ObjectId: str,
            Table: lambda v: v.dict(),  
            Column: lambda v: v.dict()  
        }
