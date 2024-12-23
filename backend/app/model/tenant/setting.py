from pydantic import BaseModel, Field, root_validator
from typing import Optional, Dict, Any

class Setting(BaseModel):
    setting_description: Optional[str] = ""
    setting_basic_name: str
    setting_default_value: Optional[str] = None
    setting_value: str
    is_custom_setting: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return self.dict()
