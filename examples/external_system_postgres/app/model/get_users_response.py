from pydantic import BaseModel
from typing import Dict

class GetUsersResponse(BaseModel):
    user_identifier: str
    custom_fields: Dict[str, str] 
