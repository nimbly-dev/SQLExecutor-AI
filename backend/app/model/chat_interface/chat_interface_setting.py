from typing import Dict, Optional
from pydantic import BaseModel

class ChatInterfaceSetting(BaseModel):
    setting_description: Optional[str] = ""
    setting_basic_name: str
    setting_toggle: bool