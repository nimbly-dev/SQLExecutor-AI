from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, List
from bson import ObjectId
from model.schema.context import ContextSetting
from model.schema.schema_chat_interface_integration_setting import SchemaChatInterfaceIntegrationSetting
from model.schema.table import Table, Column 

class Schema(BaseModel):
    tenant_id: str = Field(..., max_length=36)
    _id: Optional[str]
    schema_name: str
    description: str
    exclude_description_on_generate_sql: bool
    tables: Dict[str, Table]
    filter_rules: Optional[List[str]] = []
    synonyms: Optional[List[str]] = []
    context_type: str
    context_setting: ContextSetting
    schema_chat_interface_integration: Optional[SchemaChatInterfaceIntegrationSetting] = None


    class Config:
        # Encode table and column to dictionary
        json_encoders = {
            ObjectId: str,
            Table: lambda v: v.dict(),  
            Column: lambda v: v.dict()  
        }
