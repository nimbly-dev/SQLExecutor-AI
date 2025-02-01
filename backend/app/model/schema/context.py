from pydantic import BaseModel, root_validator, ValidationError
from typing import Optional, List


class SQLContext(BaseModel):
    table: str
    user_identifier: str
    custom_fields: List[str]
    custom_get_context_query: Optional[str] = None  

class APIContext(BaseModel):
    get_user_endpoint: str
    user_identifier: str
    custom_fields: List[str]
    auth_method: str
        
class ContextSetting(BaseModel):
    sql_context: Optional[SQLContext] = None
    api_context: Optional[APIContext] = None
