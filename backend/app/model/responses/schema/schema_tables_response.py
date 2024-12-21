from pydantic import BaseModel
from typing import List, Dict

class ColumnResponse(BaseModel):
    column_name: str
    type: str
    description: str = None
    constraints: List[str] = []
    is_sensitive_column: bool = False
    exclude_description_on_generate_sql: bool = False
    synonyms: List[str] = []

class TableResponse(BaseModel):
    table_name: str
    columns: List[ColumnResponse]
    synonyms: List[str] = []

class SchemaTablesResponse(BaseModel):
    schema_name: str
    tables: List[TableResponse]