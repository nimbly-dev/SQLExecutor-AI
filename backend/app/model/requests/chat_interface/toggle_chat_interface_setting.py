from typing import Dict, Optional
from pydantic import BaseModel

class UpdateChatInterfaceSettingRequest(BaseModel):
    setting_toggle: bool