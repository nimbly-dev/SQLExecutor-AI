from pydantic import BaseModel, validator
from typing import Optional

class SchemaChatInterfaceIntegrationSetting(BaseModel):
    enabled: bool  
    get_contexts_query: Optional[str] = None  
    get_contexts_count_query: Optional[str] = None  

    @validator("get_contexts_query", "get_contexts_count_query", always=True)
    def validate_queries(cls, v, values, field):
        if values.get("enabled") and not v:
            raise ValueError(f"{field.name} must be provided when chat_interface_integration is enabled.")
        return v