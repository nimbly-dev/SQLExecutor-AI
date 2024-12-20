import logging
from fastapi import HTTPException
from utils.ruleset.ruleset_utils import resolve_field
from utils.ruleset.ruleset_condition_utils import format_value, normalize_condition
import re
from typing import Dict, Optional, Tuple, Set

class RulesetConditionsService:

    @staticmethod
    def evaluate_condition(condition: str, session_data: dict) -> bool:
        """
        Evaluate a condition dynamically by replacing placeholders with session data.
        """
        try:
            placeholders = re.findall(r"\$\{jwt\.[a-zA-Z0-9_.]+\}", condition)
            resolved_condition = condition

            for placeholder in placeholders:
                field_path = placeholder.strip("${}").replace("jwt.", "")
                value = resolve_field(session_data, field_path)

                if value is None:
                    logging.warning(f"Field {field_path} not found in session data.")
                    resolved_value = "None"
                else:
                    resolved_value = format_value(value)

                resolved_condition = resolved_condition.replace(placeholder, resolved_value)

            resolved_condition = normalize_condition(resolved_condition)
            logging.debug(f"Final Resolved Condition: {resolved_condition}")
            return eval(resolved_condition)

        except Exception as e:
            logging.error(f"Error evaluating condition: {condition} | Resolved: {resolved_condition} | Error: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid condition: {resolved_condition} | Error: {str(e)}"
            )

    @staticmethod
    def resolve_condition(condition: str, session_data: dict, conditions_dict: Optional[Dict[str, str]]) -> str:
        """
        Resolve named conditions and placeholders recursively.

        Args:
            condition (str): Condition string with placeholders (e.g., ${jwt.custom_fields.active}).
            session_data (dict): The session data containing JWT and user-specific information.
            conditions_dict (dict): Named conditions dictionary from the ruleset.

        Returns:
            str: Fully resolved condition string or "True" if condition is None.
        """
        if not condition:
            return "True"

        # Resolve named conditions like ${conditions.is_active_user}
        while "${conditions." in condition:
            matches = re.findall(r"\$\{conditions\.([a-zA-Z0-9_]+)\}", condition)
            for match in matches:
                condition_key = match.strip()
                if not conditions_dict or condition_key not in conditions_dict:
                    logging.error(f"Condition '{condition_key}' is not defined in the ruleset.")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Condition '{condition_key}' is not defined in the ruleset."
                    )
                resolved_value = conditions_dict[condition_key]
                condition = condition.replace(f"${{conditions.{condition_key}}}", resolved_value)

        # Resolve JWT placeholders like ${jwt.custom_fields.active}
        while "${jwt." in condition:
            matches = re.findall(r"\$\{jwt\.([a-zA-Z0-9_.]+)\}", condition)
            for match in matches:
                field_path = match.strip()
                value = resolve_field(session_data, field_path)

                if value is None:
                    logging.error(f"Field '{field_path}' not found in session data.")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Field '{field_path}' is not found in session data."
                    )
                resolved_value = format_value(value)
                condition = condition.replace(f"${{jwt.{field_path}}}", resolved_value)

        resolved_condition = normalize_condition(condition)
        logging.debug(f"Resolved Condition: {resolved_condition}")
        return resolved_condition

    @staticmethod
    def merge_column_access(global_rule, group_rule_columns, user_rule, table_schema) -> Tuple[Set[str], Set[str]]:
        """
        Merge column allows/denies based on global, user-specific, and group policies.
        User-specific rules override group rules but respect global rules.

        Args:
            global_rule: Global access policy for the table.
            group_rule_columns: Group access policy's column rules for the table.
            user_rule: User-specific access policy for the table.
            table_schema: Schema of the table, including its columns.

        Returns:
            Tuple[Set[str], Set[str]]: Final allowed and denied columns.
        """
        allowed_columns = set()
        denied_columns = set()

        # Process Global Rule (highest priority)
        if global_rule:
            allowed_columns.update(global_rule.columns.allow)
            denied_columns.update(global_rule.columns.deny)

        # Process User-Specific Rule (overrides group rules but respects global rules)
        if user_rule:
            user_allowed = set(user_rule.columns.allow)
            user_denied = set(user_rule.columns.deny)

            # Resolve wildcards for user rules
            if "*" in user_allowed:
                user_allowed = set(table_schema.columns.keys())
            if "*" in user_denied:
                user_denied = set(table_schema.columns.keys())

            allowed_columns = (allowed_columns & user_allowed)  # Intersection with global allows
            denied_columns.update(user_denied)  # Merge user-specific denies

        # Process Group Rule
        if group_rule_columns and not user_rule:
            group_allowed = set(group_rule_columns.allow)
            group_denied = set(group_rule_columns.deny)

            # Resolve wildcards for group rules
            if "*" in group_allowed:
                group_allowed = set(table_schema.columns.keys())
            if "*" in group_denied:
                group_denied = set(table_schema.columns.keys())

            allowed_columns.update(group_allowed)
            denied_columns.update(group_denied)

        # Ensure denies are not overridden
        final_allowed_columns = allowed_columns - denied_columns

        logging.debug(f"Final Allowed Columns: {final_allowed_columns}")
        logging.debug(f"Final Denied Columns: {denied_columns}")

        return final_allowed_columns, denied_columns

    @staticmethod
    def _resolve_table_references(condition: str, session_data: dict) -> str:
        """
        Resolve table references (e.g., `customers.customer_id`) by replacing them with mock values or session data.
        """
        table_column_pattern = r"\b[a-zA-Z_]+\.[a-zA-Z_]+\b"
        matches = re.findall(table_column_pattern, condition)

        for match in matches:
            resolved_value = "None"
            condition = condition.replace(match, resolved_value)

        return condition
