import logging

from model.ruleset.ruleset import Ruleset
from model.tenant.tenant import Tenant
from model.authentication.external_user_session_data import ExternalSessionData
from api.core.services.ruleset.ruleset_conditions_service import RulesetConditionsService
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import SQL_INJECTORS

logger = logging.getLogger(__name__)

class InjectorResolver:
    def __init__(self, session_data: ExternalSessionData, ruleset: Ruleset):
        self.session_data = session_data
        self.ruleset = ruleset

    def _matches_condition(self, condition: str) -> bool:
        """Evaluate the condition against session data."""
        try:
            resolved_condition = RulesetConditionsService.resolve_condition(
                condition=condition,
                session_data=self.session_data.dict(),
                conditions_dict=getattr(self.ruleset, "conditions", {})
            )
            return eval(resolved_condition)
        except Exception as error:
            logger.error("Condition evaluation error: %s", error)
            return False

    def _format_value(self, value):
        """Format values safely based on their type."""
        if isinstance(value, str):
            return "'" + value.replace("'", "''") + "'"
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            formatted_list = ', '.join([self._format_value(v) for v in value])
            return f"({formatted_list})"
        raise ValueError(f"Unsupported data type: {type(value)}")

    def apply_injectors(self, sql_query: str, tenant: Tenant):
        """Apply injectors to modify the SQL query and return the updated query and filters."""
        injector_filters = []

        is_dynamic_injection_enabled = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_INJECTORS,
            setting_key="DYNAMIC_INJECTION"
        )

        logger.debug("Dynamic Injection Enabled: %s", is_dynamic_injection_enabled)

        if not is_dynamic_injection_enabled:
            sql_query = sql_query.split('WHERE')[0].strip(';') + ';'
            logger.debug("Dynamic injection disabled. Removed existing WHERE clause.")

        if not self.ruleset.injectors:
            logger.debug("No injectors found in the ruleset.")
            return sql_query, None

        for injector_name, injector in self.ruleset.injectors.items():
            if not injector.enabled:
                logger.debug("Injector '%s' is disabled. Skipping.", injector_name)
                continue

            if self._matches_condition(injector.condition.condition):
                logger.debug("Injector '%s' condition matched.", injector_name)
                for table, rule in injector.tables.items():
                    if table in sql_query:
                        filter_clause = RulesetConditionsService.resolve_condition(
                            condition=rule.filters,
                            session_data=self.session_data.dict(),
                            conditions_dict=getattr(self.ruleset, "conditions", {})
                        )
                        logger.debug("Initial filter clause: %s", filter_clause)

                        for key, value in self.session_data.custom_fields.items():
                            placeholder = f"${{jwt.{key}}}"
                            resolved_value = self._format_value(value)
                            filter_clause = filter_clause.replace(placeholder, resolved_value)
                            logger.debug("Replaced placeholder '%s' with '%s'", placeholder, resolved_value)

                        injector_filters.append(filter_clause)
            else:
                logger.debug("Injector '%s' condition did not match.", injector_name)

        if injector_filters:
            injector_str = " AND ".join(injector_filters)
            logger.debug("Combined injector filters: %s", injector_str)

            if "WHERE" in sql_query.upper():
                sql_query = sql_query.rstrip(';') + f" AND {injector_str};"
                logger.debug("Appended injector filters with AND to existing WHERE clause.")
            else:
                sql_query = sql_query.rstrip(';') + f" WHERE {injector_str};"
                logger.debug("Added injector filters as a new WHERE clause.")

            return sql_query, injector_str

        logger.debug("No injector filters were applied.")
        return sql_query, None
