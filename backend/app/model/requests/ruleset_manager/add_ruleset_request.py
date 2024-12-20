from typing import Optional, Dict, List
from pydantic import BaseModel, Field, root_validator
import re

from model.group_access_policy import GroupAccessPolicy
from model.global_access_policy import GlobalAccessPolicy
from model.user_specific_access_policy import UserSpecificAccessPolicy

class AddRulesetRequest(BaseModel):
    ruleset_name: str = Field(..., min_length=8, description="Name of the ruleset (minimum 8 characters).")
    description: str = Field(..., max_length=100, description="Description of the ruleset (maximum 100 characters).")
    default_action: str = Field(..., description="Default action for unmatched rules.")
    conditions: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional global conditions for the ruleset."
    )
    global_access_policy: GlobalAccessPolicy = Field(
        ..., description="Global access policy for all users."
    )
    group_access_policy: Optional[Dict[str, GroupAccessPolicy]] = Field(
        default=None, description="Group-specific access policies."
    )
    user_specific_access_policy: Optional[List[UserSpecificAccessPolicy]] = Field(
        default=None, description="User-specific access policies."
    )

    @root_validator(pre=True)
    def validate_ruleset(cls, values):
        # Validate default_action
        default_action = values.get("default_action")
        allowed_values = {"ALLOW", "DENY"}
        if default_action.upper() not in allowed_values:
            raise ValueError(f"Invalid default_action: {default_action}. Must be one of {allowed_values}.")
        values["default_action"] = default_action.upper()

        # Validate conditions
        conditions = values.get("conditions")
        if conditions:
            if not isinstance(conditions, dict):
                raise ValueError("`conditions` must be a dictionary.")
            for key, condition in conditions.items():
                if not isinstance(condition, str):
                    raise ValueError(f"Condition '{key}' must be a string.")
                if not cls.is_valid_dynamic_condition(condition):
                    raise ValueError(f"Condition '{key}' contains invalid syntax or unsupported operators.")

        # Validate global_access_policy
        global_access_policy = values.get("global_access_policy")
        if not isinstance(global_access_policy, dict):
            raise ValueError("`global_access_policy` must be a dictionary.")
        try:
            for table_name, table_rule in global_access_policy.get("tables", {}).items():
                for column_rule in ["allow", "deny"]:
                    if "*" in table_rule["columns"].get(column_rule, []):
                        raise ValueError(f"Wildcard '*' is not allowed in global {column_rule} rules for table '{table_name}'.")
            values["global_access_policy"] = GlobalAccessPolicy(**global_access_policy)
        except Exception as e:
            raise ValueError(f"Error validating `global_access_policy`: {str(e)}")

        # Validate group_access_policy
        group_access_policy = values.get("group_access_policy")
        if group_access_policy:
            if not isinstance(group_access_policy, dict):
                raise ValueError("`group_access_policy` must be a dictionary.")
            for group_name, group_policy in group_access_policy.items():
                try:
                    group_policy_obj = GroupAccessPolicy(**group_policy)
                    # Validate criteria
                    criteria = group_policy_obj.criteria
                    if not isinstance(criteria.matching_criteria, dict):
                        raise ValueError(f"Invalid `matching_criteria` in group '{group_name}'. Must be a dictionary.")
                    # Validate condition within criteria if it exists
                    if criteria.condition:
                        # Ensure placeholders are valid by appending `== True` if necessary
                        resolved_condition = re.sub(
                            r"\$\{conditions\.[a-zA-Z0-9_]+\}",
                            lambda match: f"{match.group(0)} == True",
                            criteria.condition
                        )
                        if not cls.is_valid_dynamic_condition(resolved_condition):
                            raise ValueError(f"Invalid condition in group '{group_name}': {criteria.condition}")
                    group_access_policy[group_name] = group_policy_obj
                except Exception as e:
                    raise ValueError(f"Error validating group '{group_name}': {str(e)}")


        # Validate user_specific_access_policy
        user_specific_access_policy = values.get("user_specific_access_policy")
        if user_specific_access_policy:
            if not isinstance(user_specific_access_policy, list):
                raise ValueError("`user_specific_access_policy` must be a list.")
            validated_entries = []
            for index, item in enumerate(user_specific_access_policy):
                try:
                    validated_entries.append(UserSpecificAccessPolicy(**item))
                except Exception as e:
                    raise ValueError(f"Error validating user_specific_access_policy at index {index}: {str(e)}")
            values["user_specific_access_policy"] = validated_entries

        return values

    @staticmethod
    def is_valid_dynamic_condition(value: str) -> bool:
        """
        Validate if the condition contains supported placeholders or operators,
        and supports arrays, booleans, and single-digit numbers.

        Args:
            value (str): The condition string.

        Returns:
            bool: True if the condition is valid, False otherwise.
        """
        placeholder_pattern = r"\$\{conditions\.[a-zA-Z0-9_]+\}"
        value = re.sub(placeholder_pattern, "True", value)  

        if value in {"True", "False"}:  # Allow direct booleans
            return True

        # Valid logical and comparison operators
        valid_operators = ["==", "and", "or", "in", "not", "<", ">", "<=", ">="]
        if any(op in value for op in valid_operators):
            return True

        # Placeholder validation (e.g., "${jwt.user_id}")
        if re.search(r"\$\{jwt\.[a-zA-Z0-9_.]+\}", value):
            return True

        # Support arrays (e.g., "[1, 2, 3]" or "['admin', 'user']")
        try:
            eval_value = eval(value)
            if isinstance(eval_value, (list, int, float, bool)):
                return True
        except (SyntaxError, NameError):
            pass

        return False

