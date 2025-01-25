from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime


class ExternalSessionDataSetting(BaseModel):
    setting_description: Optional[str] = ""
    setting_basic_name: str
    setting_value: str