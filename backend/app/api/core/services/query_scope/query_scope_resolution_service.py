import logging
from typing import List, Dict, Any, Union
from fastapi import HTTPException

from model.authentication.external_user_session_data import ExternalSessionData
from model.query_scope.query_scope import QueryScope
from model.schema.schema import Schema
from model.tenant.tenant import Tenant
from model.responses.schema.schema_tables_response import SchemaTablesResponse
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.post_process_query_scope_settings_utils import PostProcessQueryScopeSettingsUtils
from utils.query_scope.query_scope_utils import expand_columns
from utils.tenant_manager.setting_utils import SettingUtils
from utils.session.session_utils import get_session_setting
from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, SQL_GENERATION_KEY

logger = logging.getLogger(__name__)


class QueryScopeResolutionService:
    """
    Service responsible for matching the best schema for the QueryScope
    and performing final processing such as removing missing/sensitive columns
    and expanding wildcards.
    """

    @staticmethod
    async def match_schema( tenant_id: str, schemas: 
                            List[SchemaTablesResponse], 
                            query_scope: QueryScope, 
                            tenant_settings: Dict[str, Any]) -> Union[Dict[str, List[str]], Any]:
        """
        Match a user's QueryScope to the best available schema(s) based on
        discovered or known schema info.
        Returns a single Schema object or raises an HTTPException if multiple
        or no matches are found.
        """
        matched_result = SchemaDiscoveryService.get_best_matching_schemas(
            query_scope=query_scope,
            schemas=schemas,
            tenant_settings=tenant_settings
        )

        # Single match as a string
        if isinstance(matched_result, str):
            return await SchemaManagerService.get_schema(
                tenant_id=tenant_id,
                schema_name=matched_result
            )

        # Single match as a list with exactly one element
        if isinstance(matched_result, list) and len(matched_result) == 1:
            return await SchemaManagerService.get_schema(
                tenant_id=tenant_id,
                schema_name=matched_result[0]
            )

        # Multiple matches not supported
        if isinstance(matched_result, list) and len(matched_result) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple Schemas matched, SQLExecutor does not currently support this"
            )

        # No matches found
        raise HTTPException(
            status_code=404,
            detail="No matching schemas found."
        )

    @staticmethod
    def process_query_scope(
        matched_schema: Schema, 
        query_scope: QueryScope, 
        session_data: ExternalSessionData, 
        settings: Dict[str, Any],
        tenant: Tenant) -> QueryScope:

        remove_missing = SettingUtils.get_setting_value(
            settings=session_data.session_settings,
            category_key=SQL_GENERATION_KEY,
            setting_key="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE"
        )
        ignore_wildcards = SettingUtils.get_setting_value(
            settings=session_data.session_settings,
            category_key=SQL_GENERATION_KEY,
            setting_key="IGNORE_COLUMN_WILDCARDS"
        )
        remove_sensitive = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_GENERATION_KEY,
            setting_key="REMOVE_SENSITIVE_COLUMNS"
        )

        missing_columns = []

        # Expand wildcard columns first
        if not ignore_wildcards:
            schema_columns = {
                t_name: [col for col, data in tbl.columns.items() if not data.is_sensitive_column]
                for t_name, tbl in matched_schema.tables.items()
            }

            expanded_cols = []
            for col in query_scope.entities.columns:
                if col.endswith(".*"):
                    table_name = col.split(".*")[0]
                    if table_name in schema_columns:
                        expanded_cols.extend([f"{table_name}.{c}" for c in schema_columns[table_name]])
                else:
                    expanded_cols.append(col)

            query_scope.entities.columns = list(expanded_cols)
        else:
            query_scope.entities.columns = [
                col for col in query_scope.entities.columns if not col.endswith(".*")
            ]

        # Remove sensitive columns AFTER expansion
        if remove_sensitive:
            schema_sensitive_columns = {
                f"{table_name}.{col_name}"
                for table_name, table in matched_schema.tables.items()
                for col_name, col in table.columns.items()
                if col.is_sensitive_column
            }
            query_scope.entities.columns = [
                c for c in query_scope.entities.columns
                if c not in schema_sensitive_columns
            ]

        # Remove missing columns if requested
        if remove_missing:
            query_scope, missing_columns = PostProcessQueryScopeSettingsUtils.remove_missing_columns_from_query_scope(
                matched_schema, query_scope=query_scope
            )

        # Check if any columns remain
        if not query_scope.entities.columns:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "No valid columns remain after processing the input query. The requested columns do not match the schema.",
                    "matched_schema": f"{matched_schema.schema_name}",
                    "missing_columns": missing_columns
                }
            )

        return query_scope

