from pydantic import BaseModel, root_validator
from typing import Union, List

class GroupAccessColumnRule(BaseModel):
    allow: Union[str, List[str]]
    deny: List[str]

    @root_validator(pre=True)
    def validate_column_rule(cls, values):
        allow = values.get("allow")
        deny = values.get("deny")
        if allow is None or deny is None:
            raise ValueError("Both 'allow' and 'deny' must be specified in 'columns'.")
        return values