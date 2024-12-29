import logging
from typing import Dict, Any
from fastapi import HTTPException

from api.core.services.ruleset.ruleset_conditions_service import RulesetConditionsService
from model.authentication.external_user_session_data import ExternalSessionData
from model.ruleset.ruleset import Ruleset
from model.query_scope.query_scope import QueryScope
from model.schema.schema import Schema

class AccessControlResolver:
    def __init__(self, session_data: ExternalSessionData, ruleset: Ruleset, matched_schema: Schema):
        """
        Initialize the AccessControlResolver with session data and the ruleset.

        Args:
            session_data (SessionData): Current session details (e.g., user_id, roles).
            ruleset (Ruleset): Parsed ruleset model.
            matched_schema (Schema): Matched schema for the query.
        """
        self.session_data = session_data
        self.ruleset = ruleset
        self.conditions = ruleset.conditions or {} 
        self.global_policy = ruleset.global_access_policy
        self.group_policy = ruleset.group_access_policy or {}
        self.user_policy = self._get_user_specific_policy()
        self.schema = matched_schema

    def _get_user_specific_policy(self) -> Dict[str, Any]:
        """
        Fetch user-specific policy from the ruleset if it exists for the current user.
        """
        if not self.ruleset.user_specific_access_policy:
            return {}

        for policy in self.ruleset.user_specific_access_policy:
            if policy.user_identifier == self.session_data.user_id:
                logging.debug(f"User-specific policy found for user '{self.session_data.user_id}'")
                return policy.tables
        return {}

    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a condition dynamically using the RulesetConditionsService.
        """
        try:
            resolved_condition = RulesetConditionsService.resolve_condition(
                condition, self.session_data.dict(), self.conditions
            )
            result = RulesetConditionsService.evaluate_condition(resolved_condition, self.session_data.dict())
            logging.debug(f"Condition '{condition}' evaluated to: {result}")
            return result
        except Exception as e:
            logging.error(f"Error evaluating condition '{condition}': {e}")
            raise

    def _validate_table_access(self, table_name: str) -> None:
        """
        Validate access to a table based on global, group, and user-specific policies.
        """
        # Check Global Policy
        global_rule = self.global_policy.tables.get(table_name)
        if global_rule and table_name in global_rule.columns.deny:
            logging.warning(f"Access to table '{table_name}' is denied by global policy.")
            raise HTTPException(
                status_code=403,
                detail=f"Access to table '{table_name}' is denied by global policy."
            )

        # Check User-Specific Policy
        user_rule = self.user_policy.get(table_name)
        if user_rule:
            logging.debug(f"User-specific policy matched for table '{table_name}'.")
            return

        # Check Group Policy
        group_rule = self._match_group_policy(table_name)
        if group_rule:
            logging.debug(f"Group policy '{group_rule.description}' matched for table '{table_name}'.")
            return

        # Deny if no policy allows access
        logging.warning(f"Access to table '{table_name}' is denied.")
        raise HTTPException(
            status_code=403,
            detail=f"Access to table '{table_name}' is denied."
        )

    def _validate_column_access(self, table_name: str, column_name: str) -> None:
        """
        Validate access to a specific column based on global, user-specific, and group policies.
        """
        global_rule = self.global_policy.tables.get(table_name)
        user_rule = self.user_policy.get(table_name)
        group_rule = self._match_group_policy(table_name)

        allowed_columns, denied_columns = RulesetConditionsService.merge_column_access(
            global_rule,
            group_rule.tables.get(table_name).columns if group_rule else None,
            user_rule,
            self.schema.tables[table_name]
        )

        if column_name in denied_columns:
            logging.warning(f"Access to column '{column_name}' in table '{table_name}' is denied.")
            raise HTTPException(
                status_code=403,
                detail=f"Access to column '{column_name}' in table '{table_name}' is denied."
            )

        if allowed_columns and column_name not in allowed_columns:
            logging.warning(f"Access to column '{column_name}' in table '{table_name}' is not explicitly allowed.")
            raise HTTPException(
                status_code=403,
                detail=f"Access to column '{column_name}' in table '{table_name}' is not explicitly allowed."
            )

        logging.debug(f"Access to column '{column_name}' in table '{table_name}' is allowed.")

    def _validate_matching_criteria(self, matching_criteria: Dict[str, Any]) -> bool:
        """
        Validate if the current session data matches the provided matching criteria.
        """
        logging.debug(f"Evaluating Matching Criteria: {matching_criteria}")
        for key, value in matching_criteria.items():
            session_value = self.session_data.custom_fields.get(key, [])
            
            # Ensure session_value is treated as a list for comparison
            if not isinstance(session_value, list):
                session_value = [session_value]
            
            # Compare values
            if isinstance(value, list):
                if not set(value).intersection(session_value):
                    logging.debug(f"Criteria mismatch for key '{key}': Expected {value}, Found {session_value}")
                    return False
            elif session_value[0] != value:  # Handle single non-list values
                logging.debug(f"Criteria mismatch for key '{key}': Expected {value}, Found {session_value[0]}")
                return False

        return True

    def _match_group_policy(self, table_name: str):
        """
        Match the first applicable group policy based on matching criteria and conditions.
        """
        for group_name, group_rule in self.group_policy.items():
            logging.debug(f"Evaluating Group: {group_name}")

            if not self._validate_matching_criteria(group_rule.criteria.matching_criteria):
                logging.debug(f"Matching criteria failed for group '{group_name}'")
                continue

            if group_rule.criteria.condition and not self._evaluate_condition(group_rule.criteria.condition):
                logging.debug(f"Condition failed for group '{group_name}'")
                continue

            if table_name in group_rule.tables:
                logging.debug(f"Group '{group_name}' matched for table '{table_name}'.")
                return group_rule

        logging.debug("No group policy matched.")
        return None

    def has_access_to_scope(self, query_scope: QueryScope) -> bool:
        """
        Validate access to the entire query scope and deny if any table or column fails access control.
        """
        denied_tables = []
        denied_columns = []

        for table in query_scope.entities.tables:
            try:
                self._validate_table_access(table)
            except HTTPException as e:
                logging.debug(f"Access denied for table: {table}")
                denied_tables.append(table)
                continue

            table_columns = [
                column for column in query_scope.entities.columns if column.startswith(f"{table}.")
            ]
            for column in table_columns:
                column_name = column.split(".", 1)[1]
                try:
                    self._validate_column_access(table, column_name)
                except HTTPException as e:
                    logging.debug(f"Access denied for column: {column}")
                    denied_columns.append(column)

        if denied_tables or denied_columns:
            logging.warning(f"Access denied for tables: {denied_tables}, columns: {denied_columns}")
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Access denied for certain tables or columns.",
                    "denied_tables": denied_tables,
                    "denied_columns": denied_columns
                }
            )

        logging.debug("Access granted for all tables and columns.")
        return True
