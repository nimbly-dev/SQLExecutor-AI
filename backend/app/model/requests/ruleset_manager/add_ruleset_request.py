from typing import Optional, Dict, List
from pydantic import BaseModel, Field, validator

from model.user_specific_access_policy import UserSpecificAccessPolicy

class AddRulesetRequest(BaseModel):
    ruleset_name: str
    description: str
    default_action: str
    global_access_policy: Dict[str, Dict]
    table_access_policy: Dict[str, Dict]
    user_specific_access_policy: Optional[List[UserSpecificAccessPolicy]] = None 

    @validator("default_action", pre=True, always=True)
    def ensure_uppercase_default_action(cls, value):
        if value is None:
            return value
        return value.upper()

    @validator("default_action")
    def validate_default_action(cls, value):
        allowed_values = {"ALLOW", "DENY"}
        if value not in allowed_values:
            raise ValueError(f"Invalid default_action: {value}. Must be one of {allowed_values}.")
        return value

    @validator("ruleset_name")
    def validate_ruleset_name_length(cls, value):
        if len(value) < 8:
            raise ValueError("ruleset_name must be at least 8 characters long.")
        return value

    @validator("description")
    def validate_description_length(cls, value):
        if len(value) > 100:
            raise ValueError("description must not exceed 100 characters.")
        return value

    @validator("global_access_policy", "table_access_policy", pre=True, always=True)
    def validate_policy(cls, value, field):
        """
        Validate the `tables` key for `global_access_policy` and `table_access_policy`.
        """
        if value is None:
            return value
        if not isinstance(value, dict):
            raise ValueError(f"{field.name} must be a dictionary.")
        if "tables" not in value:
            raise ValueError(f"{field.name} must contain a 'tables' key.")
        tables = value["tables"]
        if not isinstance(tables, dict):
            raise ValueError(f"The 'tables' key in {field.name} must be a dictionary.")
        for table_name, table_policy in tables.items():
            if not isinstance(table_policy, dict):
                raise ValueError(f"Table '{table_name}' in {field.name} must be a dictionary.")
            if "columns" not in table_policy or "condition" not in table_policy:
                raise ValueError(
                    f"Table '{table_name}' in {field.name} must contain 'columns' and 'condition' keys."
                )
        return value

    @validator("user_specific_access_policy", pre=True, always=True)
    def validate_user_specific_policy(cls, value):
        """
        Validate the `user_specific_access_policy`.
        """
        if value is None:
            return value
        if not isinstance(value, list):
            raise ValueError("user_specific_access_policy must be a list.")
        for item in value:
            if not isinstance(item, dict):
                raise ValueError("Each entry in user_specific_access_policy must be a dictionary.")
            if not isinstance(item.get("user_identifier"), str):  # Updated field name
                raise ValueError("The 'user_identifier' field in each entry of user_specific_access_policy must be a string.")
            if "tables" not in item:
                raise ValueError("Each entry in user_specific_access_policy must contain a 'tables' key.")
            tables = item["tables"]
            if not isinstance(tables, dict):
                raise ValueError("The 'tables' key in user_specific_access_policy must be a dictionary.")
            for table_name, table_policy in tables.items():
                if not isinstance(table_policy, dict):
                    raise ValueError(f"Table '{table_name}' in user_specific_access_policy must be a dictionary.")
                if "columns" not in table_policy or "condition" not in table_policy:
                    raise ValueError(
                        f"Table '{table_name}' in user_specific_access_policy must contain 'columns' and 'condition' keys."
                    )
        return value
