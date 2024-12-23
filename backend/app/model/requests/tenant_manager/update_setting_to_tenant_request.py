from pydantic import BaseModel, validator, Field
from typing import Dict, List
from model.tenant.setting import Setting

class UpdateSettingRequest(BaseModel):
    __root__: Dict[str, Setting]

    def dict(self, *args, **kwargs):
        return super().dict(*args, **kwargs)["__root__"]