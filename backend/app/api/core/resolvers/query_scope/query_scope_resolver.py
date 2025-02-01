# query_scope_resolver.py

import logging
from typing import List, Dict, Any, Union
from fastapi import HTTPException

from model.external_system_integration.external_user_session_data import ExternalSessionData
from model.query_scope.query_scope import QueryScope
from model.responses.sql_generation.sql_generation_error import QueryScopeResolutionErrorResponse, QueryScopeErrorType
from model.schema.schema import Schema
from model.tenant.tenant import Tenant
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.services.query_scope.query_scope_preparation_service import QueryScopePreparationService
from api.core.services.query_scope.query_scope_resolution_service import QueryScopeResolutionService
from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, SQL_GENERATION_KEY

logger = logging.getLogger(__name__)

class QueryScopeResolver:
    """
    Entrypoint for resolving the QueryScope output from the LLM model.
    Utilizes two consolidated services:
        - QueryScopePreparationService
        - QueryScopeResolutionService
    to handle schema fetching, soft preprocessing, matching, and final processing.
    """

    def __init__(self, session_data: ExternalSessionData, settings: Dict[str, Any], query_scope: QueryScope, tenant: Tenant):
        self.session_data : ExternalSessionData= session_data
        self.settings = settings or {}
        self.query_scope = query_scope
        self.schemas = []
        self.tenant = tenant

    async def match_user_query_to_schema(self, tenant_id: str) -> Union[Dict[str, List[str]], Any]:
        """
        Fetch and validate schemas, then match the query scope to the most relevant
        schema(s) and return the appropriate response.
        """
        self.schemas = await QueryScopePreparationService.prepare_query_scope(
            tenant_id=tenant_id,
            query_scope=self.query_scope
        )

        tenant_settings = {}
        return await QueryScopeResolutionService.match_schema(
            tenant_id=tenant_id,
            schemas=self.schemas,
            query_scope=self.query_scope,
            tenant_settings=tenant_settings
        )

    def resolve_query_scope(self, matched_schema: Schema) -> QueryScope:
        """
        Args:
            matched_schema (Schema): The schema to match against the query scope.
        Returns:
            QueryScope: The resolved query scope with corrected table and column names.
        Raises:
            HTTPException: If any of the following errors occur:
                - No columns remain after expansion or filtering
        """
        remove_missing_columns = getattr(
            self.session_data.session_settings.get("SQL_GENERATION", {}).get("REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE", None), 
            "setting_value", 
            False
        )
        remove_sensitive = SettingUtils.get_setting_value(
            settings=self.tenant.settings,
            category_key=POST_PROCESS_QUERYSCOPE_CATEGORY_KEY,
            setting_key="REMOVE_SENSITIVE_COLUMNS"
        )

        sensitive_columns: List[str] = []
        corrected_table_map: Dict[str, str] = {}
        corrected_tables: List[str] = []
            
        # Resolve Table Names
        for table in self.query_scope.entities.tables:
            best_table_match = QueryScopeResolutionService.find_best_match_table(table, matched_schema)
            if best_table_match:
                corrected_table_map[table] = best_table_match
                corrected_tables.append(best_table_match)
            else:
                error_response = QueryScopeResolutionErrorResponse(
                    scope_error_type=QueryScopeErrorType.TABLE_NOT_FOUND,
                    user_query_scope=self.query_scope,
                    issues=[{
                        "type": "missing_table",
                        "reason": f"The table '{table}' does not exist."
                    }],
                    suggestions=["Verify the table name or consult the schema documentation."],
                    message=f"Query scope resolution failed due to missing table '{table}'."
                )
                raise HTTPException(status_code=400, detail=error_response.dict())

        self.query_scope.entities.tables = corrected_tables

        # Resolve Columns
        corrected_columns: List[str] = []
        for col in self.query_scope.entities.columns:
            if "." not in col:
                error_response = QueryScopeResolutionErrorResponse(
                    scope_error_type=QueryScopeErrorType.COLUMN_NOT_QUALIFIED,
                    user_query_scope=self.query_scope,
                    issues=[{
                        "type": "unqualified_column",
                        "reason": f"Column '{col}' must be qualified as 'table.column'."
                    }],
                    suggestions=["Qualify the column with the table name, e.g., 'table.column'."],
                    message=f"Query scope resolution failed due to unqualified column '{col}'."
                )
                raise HTTPException(status_code=400, detail=error_response.dict())

            old_table, column_name = col.split(".", 1)
            new_table = corrected_table_map.get(old_table, old_table)

            if new_table not in matched_schema.tables:
                error_response = QueryScopeResolutionErrorResponse(
                    scope_error_type=QueryScopeErrorType.TABLE_NOT_FOUND,
                    user_query_scope=self.query_scope,
                    issues=[{
                        "type": "missing_table",
                        "reason": f"The table '{new_table}' does not exist."
                    }],
                    suggestions=["Verify the table name or consult the schema documentation."],
                    message=f"Query scope resolution failed because table '{new_table}' is invalid."
                )
                raise HTTPException(status_code=400, detail=error_response.dict())

            # Check for wildcard
            if column_name == "*":
                # Use service-level expansion
                expanded = QueryScopeResolutionService.expand_wildcard_columns(
                    table_name=new_table,
                    schema=matched_schema,
                    remove_sensitive=remove_sensitive
                )
                # The call above already removes sensitive columns if remove_sensitive is True
                # so just extend
                corrected_columns.extend(expanded)
                continue

            # Non-wildcard columns
            table_columns = matched_schema.tables[new_table].columns
            if column_name not in table_columns:
                best_match = QueryScopeResolutionService.find_best_match_column_using_synonyms(
                    table_name=new_table,
                    column_name=column_name,
                    schema=matched_schema
                )
                if best_match:
                    corrected_columns.append(best_match)
                    continue
                
                # If column does not exist, skip it when remove_missing_columns=True
                if column_name not in table_columns:
                    if remove_missing_columns:
                        continue  # Skip this column
                    else:
                        error_response = QueryScopeResolutionErrorResponse(
                            scope_error_type=QueryScopeErrorType.COLUMN_NOT_FOUND,
                            user_query_scope=self.query_scope,
                            issues=[{
                                "type": "missing_column",
                                "reason": f"The column '{column_name}' does not exist in table '{new_table}'."
                            }],
                            suggestions=["Verify the column name or consult the schema documentation."],
                            message=f"Query scope resolution failed due to missing column '{column_name}' in table '{new_table}'."
                        )
                        raise HTTPException(status_code=400, detail=error_response.dict())

            if remove_sensitive and column_name in table_columns and table_columns[column_name].is_sensitive_column:
                sensitive_columns.append(f"{new_table}.{column_name}")
                continue

            corrected_columns.append(f"{new_table}.{column_name}")

        self.query_scope.entities.columns = corrected_columns
        self.query_scope.entities.sensitive_columns = sensitive_columns

        # Optionally remove columns that don't exist in schema
        if remove_missing_columns:
            self.query_scope, missing_cols = QueryScopeResolutionService.remove_missing_columns_from_query_scope(
                schema=matched_schema,
                query_scope=self.query_scope
            )

        # Ensure at least one column remains
        if not self.query_scope.entities.columns:
            error_response = QueryScopeResolutionErrorResponse(
                scope_error_type=QueryScopeErrorType.NO_COLUMN_REMAIN,
                user_query_scope=self.query_scope,
                issues=[{
                    "type": "missing_columns",
                    "reason": "No columns remain after expansion or filtering."
                }],
                suggestions=["Specify valid columns or check table/column names."],
                sensitive_columns_removed=sensitive_columns,
                message="Query scope resolution failed due to unresolved inputs."
            )
            raise HTTPException(status_code=400, detail=error_response.dict())

        return self.query_scope