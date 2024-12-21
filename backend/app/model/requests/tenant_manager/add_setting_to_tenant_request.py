from pydantic import BaseModel, validator, Field
from typing import Dict, List
from model.setting import Setting 

import re

class AddSettingToTenantRequest(BaseModel):
    __root__: Dict[str, Dict[str, Setting]]

    def dict(self, *args, **kwargs):
        return super().dict(*args, **kwargs)["__root__"]

    @validator("__root__")
    def validate_keys(cls, values):
        """
        Ensure that all keys are uppercase, alphanumeric or underscores only.
        """
        pattern = re.compile(r"^[A-Z0-9_]+$")
        for key in values.keys():
            if not pattern.match(key):
                raise ValueError(
                    f"Invalid setting category key: '{key}'. Keys must be uppercase and contain only letters, numbers, or underscores."
                )
        return values
