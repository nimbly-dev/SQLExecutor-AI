from pydantic import BaseModel
from typing import List, Dict

class ColumnResponse(BaseModel):
    column_name: str  
    type: str         
    description: str = None  
    constraints: List[str] = [] 

class TableResponse(BaseModel):
    table_name: str
    columns: List[ColumnResponse] 

class SchemaTablesResponse(BaseModel):
    schema_name: str
    tables: List[TableResponse]  