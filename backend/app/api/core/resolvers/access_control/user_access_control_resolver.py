import logging
from typing import Dict, Any, Tuple, Optional, List
from fastapi import HTTPException

from api.core.services.ruleset.ruleset_conditions_service import RulesetConditionsService
from model.external_system_integration.external_user_session_data import ExternalSessionData
from model.responses.sql_generation.sql_generation_error import ErrorType, AccessControlViolationResponse, AccessViolation, AccessViolationType
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

    def _validate_table_access(self, table_name: str) -> Optional[AccessViolation]:
        """
        Validate access to a table based on global, group, and user-specific policies.
        Returns AccessViolation if access is denied, None if allowed.
        """
        # Check Global Policy
        global_rule = self.global_policy.tables.get(table_name)
        if global_rule and table_name in global_rule.columns.deny:
            return AccessViolation(
                entity=table_name,
                policy_type="global",
                violation_type=AccessViolationType.TABLE_ACCESS_DENIED,
                reason="Table access denied by global policy",
                failed_condition="N/A"
            )

        # Check User-Specific Policy
        user_rule = self.user_policy.get(table_name)
        if user_rule:
            logging.debug(f"User-specific policy matched for table '{table_name}'.")
            return None

        # Check Group Policy
        group_rule = self._match_group_policy(table_name)
        if group_rule:
            logging.debug(f"Group policy '{group_rule.description}' matched for table '{table_name}'.")
            return None

        return AccessViolation(
            entity=table_name,
            policy_type="access",
            violation_type=AccessViolationType.MISSING_PERMISSION,
            reason="No matching access policy found for this table",
            failed_condition="Table not found in any applicable policy"
        )

    def _validate_column_access(self, table_name: str, column_name: str) -> Optional[AccessViolation]:
        """
        Validate access to a specific column based on global, user-specific, and group policies.
        Returns AccessViolation if access is denied, None if allowed.
        """
        global_rule = self.global_policy.tables.get(table_name)
        user_rule = self.user_policy.get(table_name)
        group_rule = self._match_group_policy(table_name)

        # Get group rule columns safely
        group_rule_columns = None
        if group_rule and group_rule.tables and table_name in group_rule.tables:
            group_rule_columns = group_rule.tables[table_name].columns

        allowed_columns, denied_columns = RulesetConditionsService.merge_column_access(
            global_rule,
            group_rule_columns,
            user_rule,
            self.schema.tables[table_name]
        )

        full_column_name = f"{table_name}.{column_name}"
        
        if column_name in denied_columns:
            policy_type = "global" if global_rule and column_name in global_rule.columns.deny else \
                         "user" if user_rule and column_name in user_rule.columns.deny else "group"
            policy_name = None
            if policy_type == "group" and group_rule:
                policy_name = group_rule.description
            
            return AccessViolation(
                entity=full_column_name,
                policy_type=policy_type,
                policy_name=policy_name,
                violation_type=AccessViolationType.COLUMN_ACCESS_DENIED,
                reason=f"Column access explicitly denied by {policy_type} policy",
                failed_condition=f"Column '{column_name}' is explicitly denied by policy '{policy_type}'"
            )

        if allowed_columns and column_name not in allowed_columns:
            return AccessViolation(
                entity=full_column_name,
                policy_type="access",
                violation_type=AccessViolationType.MISSING_PERMISSION,
                reason="Column access not explicitly allowed by any policy",
                failed_condition=f"Column '{column_name}' is explicitly denied by policy '{policy_type}'"
            )

        return None

    def _validate_matching_criteria(self, matching_criteria: Dict[str, Any]) -> bool:
        """
        Check if session data matches provided criteria before evaluating conditions.

        Handles type normalization for booleans, strings, and other potential mismatches.
        """
        session_dict = self.session_data.dict().get("custom_fields", {})

        for key, expected_value in matching_criteria.items():
            value_in_session = session_dict.get(key)

            # Normalize boolean values (e.g., "TRUE" -> True, "FALSE" -> False)
            if isinstance(expected_value, bool):
                if isinstance(value_in_session, str):
                    value_in_session = value_in_session.upper() == "TRUE"

            # Normalize list comparisons
            if isinstance(expected_value, list):
                if value_in_session not in expected_value:
                    logging.debug(
                        f"Criteria mismatch: {key}='{value_in_session}' not in expected values {expected_value}"
                    )
                    return False

            # Direct comparison
            else:
                if str(expected_value).lower() != str(value_in_session).lower():
                    logging.debug(
                        f"Criteria mismatch: {key}='{value_in_session}' does not match expected value '{expected_value}'"
                    )
                    return False

        return True

    def _match_group_policy(self, table_name: str):
        """
        Match the first applicable group policy based on matching criteria and conditions.
        """
        for group_name, group_rule in self.group_policy.items():
            if self._validate_matching_criteria(group_rule.criteria.matching_criteria):
                condition_str = group_rule.criteria.condition or "True"
                if self._evaluate_condition(condition_str):
                    logging.debug(f"Group policy '{group_name}' matched for table '{table_name}'.")
                    return group_rule
        logging.debug("No group policy matched.")
        return None

    def has_access_to_scope(self, query_scope: QueryScope, user_input: str = "", sql_query: str = "") -> bool:
        """
        Validate access to the entire query scope and deny if any table or column fails access control.
        """
        denied_tables = []
        denied_columns = []
        violations: List[AccessViolation] = []

        for table in query_scope.entities.tables:
            table_violation = self._validate_table_access(table)
            if table_violation:
                logging.debug(f"Access denied for table: {table}")
                denied_tables.append(table)
                violations.append(table_violation)
                continue

            table_columns = [
                column for column in query_scope.entities.columns if column.startswith(f"{table}.")
            ]
            for column in table_columns:
                column_name = column.split(".", 1)[1]
                column_violation = self._validate_column_access(table, column_name)
                if column_violation:
                    logging.debug(f"Access denied for column: {column}")
                    denied_columns.append(column)
                    violations.append(column_violation)

        if violations:
            logging.warning(f"Access violations found: {violations}")
            error_response = AccessControlViolationResponse(
                error_type=ErrorType.ACCESS_DENIED,
                user_query_scope=query_scope,
                denied_tables=denied_tables,
                denied_columns=denied_columns,
                access_violations=[
                    AccessViolation(
                        entity=v.entity,
                        policy_type=v.policy_type,
                        policy_name=v.policy_name,
                        reason=v.reason,
                        violation_type=(
                            AccessViolationType.TABLE_ACCESS_DENIED 
                            if v.entity in denied_tables 
                            else AccessViolationType.COLUMN_ACCESS_DENIED
                        ),
                        failed_condition=v.failed_condition
                    ) 
                    for v in violations
                ],
                user_input=user_input,
                sql_query=sql_query
            )
            raise HTTPException(
                status_code=403,
                detail=error_response.dict()
            )

        logging.debug("Access granted for all tables and columns.")
        return True
