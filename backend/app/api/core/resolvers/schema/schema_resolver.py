import logging
from typing import Dict

from model.schema.schema import Schema
from model.query_scope.query_scope import QueryScope
from model.query_scope.entities import Entities
from model.tenant.tenant import Tenant
from model.external_system_integration.external_user_session_data import ExternalSessionData
from model.external_system_integration.external_user_session_data_setting import ExternalSessionDataSetting
from model.schema.resolved_schema import ResolvedSchema, ResolvedColumn, ResolvedTable, ResolvedJoin
from api.core.constants.tenant.settings_categories import SCHEMA_RESOLVER_CATEGORY_KEY, SQL_GENERATION_KEY

from utils.tenant_manager.setting_utils import SettingUtils

logger = logging.getLogger(__name__)

class SchemaResolver:
    def __init__(self, session_data: ExternalSessionData, tenant: Tenant, matched_schema: Schema, query_scope: QueryScope):
        """
        Initializes the SchemaResolver with session data, tenant information, schema, and query scope.

        Args:
            session_data (SessionData): The session information including user and tenant details.
            tenant (Tenant): The tenant-specific details.
            matched_schema (Schema): The schema to be resolved.
            query_scope (QueryScope): The query scope specifying allowed tables and columns.
        """
        self.session_data = session_data
        self.tenant = tenant
        self.matched_schema = matched_schema
        self.query_scope = query_scope
        logger.info("SchemaResolver initialized.")

    def resolve_schema(self) -> Dict:
        """
        Resolves and filters the schema based on query scope, sensitivity, and exclusions.

        Returns:
            dict: A JSON object containing filtered tables and columns to be used as Context for Prompting the NLP
        """
        logger.info("Starting schema resolution.")
        resolved_tables = {}

        # Tenant-specific settings
        tenant_settings = {
            "REMOVE_SENSITIVE_COLUMNS": SettingUtils.get_setting_value(
                settings=self.tenant.settings,
                category_key=SQL_GENERATION_KEY,
                setting_key="REMOVE_SENSITIVE_COLUMNS"
            ),
            "REMOVE_ALL_DESCRIPTIONS": SettingUtils.get_setting_value(
                settings=self.tenant.settings,
                category_key=SCHEMA_RESOLVER_CATEGORY_KEY,
                setting_key="REMOVE_ALL_DESCRIPTIONS"
            ),
        }

        allowed_tables = set(self.query_scope.entities.tables) if self.query_scope and self.query_scope.entities.tables else None
        allowed_columns = set(self.query_scope.entities.columns) if self.query_scope and self.query_scope.entities.columns else None

        for table_name, table in self.matched_schema.tables.items():
            if allowed_tables and table_name not in allowed_tables:
                logger.debug(f"Skipping table {table_name} not in query scope.")
                continue

            resolved_columns = {}

            for column_name, column in table.columns.items():
                # Initialize description to avoid unbound errors
                description = column.description if column.description else None

                if allowed_columns and f"{table_name}.{column_name}" not in allowed_columns:
                    logger.debug(f"Skipping column {column_name} not in query scope.")
                    continue

                if tenant_settings["REMOVE_SENSITIVE_COLUMNS"] or column.is_sensitive_column:
                    logger.debug(f"Excluding sensitive column {column_name} due to tenant settings.")
                    continue

                # Set description conditionally based on settings and exclude_description_on_generate_sql
                if tenant_settings["REMOVE_ALL_DESCRIPTIONS"] or column.exclude_description_on_generate_sql:
                    description = None

                resolved_columns[column_name] = ResolvedColumn(
                    type=column.type,
                    description=description,
                    synonyms=column.synonyms if column.synonyms else None
                )

            resolved_relationships = {
                rel_name: ResolvedJoin(
                    description=None if tenant_settings["REMOVE_ALL_DESCRIPTIONS"] or column.exclude_description_on_generate_sql else rel.description,
                    table=rel.table,
                    on=rel.on,
                    type=rel.type
                ) for rel_name, rel in (table.relationships or {}).items()
            } if table.relationships else None

            # Handle description removal
            table_description = None if tenant_settings["REMOVE_ALL_DESCRIPTIONS"] \
                                        else table.description

            resolved_tables[table_name] = ResolvedTable(
                description=table_description,
                synonyms=table.synonyms if table.synonyms else None,
                columns=resolved_columns,
                relationships=resolved_relationships
            )

        resolved_schema = ResolvedSchema(
            tables=resolved_tables
        )
        logger.info("Schema resolution completed successfully.")
        return resolved_schema.dict(exclude_none=True, by_alias=True)

