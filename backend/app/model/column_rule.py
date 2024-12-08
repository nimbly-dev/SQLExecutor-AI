from pydantic import BaseModel, root_validator
from typing import Union, List
import re

class ColumnRule(BaseModel):
    allow: Union[str, List[str]]
    deny: List[str]
    
    _check_invalid_chars = lambda value: bool(re.search(r"[^a-zA-Z0-9_*]", value))

    @root_validator(pre=True)
    def validate_column_rule(cls, values):
        allow = values.get("allow")
        deny = values.get("deny")

        # Validate 'allow' field
        if isinstance(allow, list):
            if "*" in allow and len(allow) > 1:
                raise ValueError("Wildcard '*' cannot be used in a list for 'allow'.")
            for item in allow:
                if isinstance(item, str) and cls._check_invalid_chars(item):
                    raise ValueError(f"Invalid special characters found in 'allow': {item}")
        elif isinstance(allow, str):
            if cls._check_invalid_chars(allow):
                raise ValueError(f"Invalid special characters found in 'allow': {allow}")

        # Validate 'deny' field
        if isinstance(deny, list):
            if "*" in deny and len(deny) > 1:
                raise ValueError("Wildcard '*' cannot be used in a list for 'deny'.")
            for item in deny:
                if isinstance(item, str) and cls._check_invalid_chars(item):
                    raise ValueError(f"Invalid special characters found in 'deny': {item}")
        elif isinstance(deny, str):
            if cls._check_invalid_chars(deny):
                raise ValueError(f"Invalid special characters found in 'deny': {deny}")

        return values
