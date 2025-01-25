import logging
from typing import List, Dict, Any, Union
from fastapi import HTTPException

from model.external_system_integration.external_user_session_data import ExternalSessionData
from model.query_scope.query_scope import QueryScope
from model.responses.sql_generation.sql_generation_error import QueryScopeResolutionErrorResponse, SchemaDiscoveryErrorResponse, SchemaDiscoveryErrorType, QueryScopeErrorType
from model.schema.schema import Schema
from model.tenant.tenant import Tenant
from model.responses.schema.schema_tables_response import SchemaTablesResponse
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.post_process_query_scope_settings_utils import PostProcessQueryScopeSettingsUtils
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, SQL_GENERATION_KEY

logger = logging.getLogger(__name__)

class QueryScopeResolutionService:
    """
    Service responsible for matching the best schema for the QueryScope
    and performing final processing such as removing missing/sensitive columns
    and expanding wildcards.
    """

    @staticmethod
    async def match_schema(tenant_id: str, schemas: List[SchemaTablesResponse], query_scope: QueryScope, tenant_settings: Dict[str, Any]) -> Union[Dict[str, List[str]], Any]:
        """
        Match a user's QueryScope to the best available schema(s) based on
        discovered or known schema info.
        Wildcards (table.*) are preserved here and not expanded.
        """
        matched_result = SchemaDiscoveryService.get_best_matching_schemas(
            query_scope=query_scope,
            schemas=schemas,
            tenant_settings=tenant_settings
        )

        if isinstance(matched_result, str):
            return await SchemaManagerService.get_schema(
                tenant_id=tenant_id,
                schema_name=matched_result
            )
        if isinstance(matched_result, list) and len(matched_result) == 1:
            return await SchemaManagerService.get_schema(
                tenant_id=tenant_id,
                schema_name=matched_result[0]
            )
        if isinstance(matched_result, list) and len(matched_result) > 1:
            raise HTTPException(
                status_code=400,
                detail=SchemaDiscoveryErrorResponse(
                    discovery_error_type=SchemaDiscoveryErrorType.MULTIPLE_SCHEMAS,
                    user_query_scope=query_scope,
                    matched_schemas=matched_result,
                    suggestions=["Add more specific constraints to refine the match."],
                    message="Ambiguity detected: Multiple schemas match the query scope."
                ).dict()
            )
        raise HTTPException(
            status_code=404,
            detail=SchemaDiscoveryErrorResponse(
                discovery_error_type=SchemaDiscoveryErrorType.NO_MATCHING_SCHEMA,
                user_query_scope=query_scope,
                unmatched_tables=query_scope.entities.tables,
                suggestions=["Check your table names or use synonyms."],
                message="No schema matches the query scope."
            ).dict()
        )

    @staticmethod
    def process_query_scope(
        matched_schema: Schema, 
        query_scope: QueryScope, 
        session_data: ExternalSessionData, 
        settings: Dict[str, Any],
        tenant: Tenant
    ) -> QueryScope:
        """
        Final stage: Expand wildcards and remove sensitive or missing columns.
        """
        remove_missing_session = SettingUtils.get_setting_value(
            settings=session_data.session_settings,
            category_key=SQL_GENERATION_KEY,
            setting_key="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE"
        )
        remove_sensitive = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=POST_PROCESS_QUERYSCOPE_CATEGORY_KEY,
            setting_key="REMOVE_SENSITIVE_COLUMNS"
        )
        sensitive_columns = []

        # Always expand table.* now
        expanded_cols = []
        for col in query_scope.entities.columns:
            if col.endswith(".*"):
                t_name = col[:-2]
                if t_name not in matched_schema.tables:
                    raise HTTPException(
                        status_code=400,
                        detail=f"The table '{t_name}' does not exist."
                    )
                for column_name, col_data in matched_schema.tables[t_name].columns.items():
                    # Exclude sensitive columns after expansion if needed
                    if remove_sensitive and col_data.is_sensitive_column:
                        sensitive_columns.append(f"{t_name}.{column_name}")
                        continue
                    expanded_cols.append(f"{t_name}.{column_name}")
            else:
                # Validate table/column if possible
                if "." not in col:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Column '{col}' must be qualified as 'table.column'."
                    )
                t_name, column_name = col.split(".", 1)
                if t_name not in matched_schema.tables:
                    raise HTTPException(
                        status_code=400,
                        detail=f"The table '{t_name}' does not exist."
                    )
                if column_name not in matched_schema.tables[t_name].columns:
                    raise HTTPException(
                        status_code=400,
                        detail=f"The column '{column_name}' does not exist in table '{t_name}'."
                    )
                # Check sensitivity
                if remove_sensitive and matched_schema.tables[t_name].columns[column_name].is_sensitive_column:
                    sensitive_columns.append(f"{t_name}.{column_name}")
                    continue
                expanded_cols.append(col)

        query_scope.entities.columns = expanded_cols

        if remove_missing_session:
            query_scope, missing = PostProcessQueryScopeSettingsUtils.remove_missing_columns_from_query_scope(
                matched_schema, query_scope
            )

        if not query_scope.entities.columns:
            raise HTTPException(
                status_code=400,
                detail=QueryScopeResolutionErrorResponse(
                    scope_error_type=QueryScopeErrorType.COLUMN_NOT_FOUND,
                    user_query_scope=query_scope,
                    issues=[
                        {
                            "type": "missing_columns",
                            "reason": "No columns remain after expansion or filtering."
                        }
                    ],
                    suggestions=["Specify valid columns or check table/column names."],
                    sensitive_columns_removed=sensitive_columns,
                    message="Query scope resolution failed due to unresolved inputs."
                ).dict()
            )

        return query_scope

