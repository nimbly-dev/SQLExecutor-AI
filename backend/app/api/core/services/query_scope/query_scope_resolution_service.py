# query_scope_resolution_service.py

import difflib
import logging
from typing import List, Dict, Any, Union, Optional
from fastapi import HTTPException

from model.external_system_integration.external_user_session_data import ExternalSessionData
from model.query_scope.query_scope import QueryScope
from model.responses.schema.schema_tables_response import SchemaTablesResponse
from model.responses.sql_generation.sql_generation_error import SchemaDiscoveryErrorResponse, SchemaDiscoveryErrorType
from model.schema.schema import Schema
from model.tenant.tenant import Tenant
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, SQL_GENERATION_KEY

logger = logging.getLogger(__name__)

class QueryScopeResolutionService:
    """
    Service responsible for:
      - Matching the best schema for the QueryScope
      - Utility methods for final processing:
        e.g., removing missing/sensitive columns, expanding wildcards, etc.
    """

    @staticmethod
    async def match_schema(
        tenant_id: str,
        schemas: List[SchemaTablesResponse],
        query_scope: QueryScope,
        tenant_settings: Dict[str, Any]
    ) -> Union[Dict[str, List[str]], Any]:
        """
        Match a user's QueryScope to the best available schema(s) based on
        discovered or known schema info. Returns a single matched Schema object
        or raises an exception if multiple or none are matched.
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
    def remove_missing_columns_from_query_scope(schema: Schema, query_scope: QueryScope):
        """
        Example logic that checks which columns don't exist and removes them.
        Returns the (modified query_scope, missing_columns_list).
        """
        existing_columns = []
        missing_columns = []

        for col in query_scope.entities.columns:
            t_name, c_name = col.split(".", 1)
            if t_name in schema.tables and c_name in schema.tables[t_name].columns:
                existing_columns.append(col)
            else:
                missing_columns.append(col)

        query_scope.entities.columns = existing_columns
        return query_scope, missing_columns

    @staticmethod
    def find_best_match_table(table_name: str, schema: Schema) -> Optional[str]:
        """
        Find the best matching table name in the schema using synonyms and fuzzy matching.
        Returns the corrected table name or None if no match is found.
        """

        # Direct table match
        if table_name in schema.tables:
            return table_name

        # Build a mapping of synonyms -> actual table name
        table_synonym_map = {}
        table_candidates = list(schema.tables.keys())
        for tbl_name, tbl_data in schema.tables.items():
            for synonym in tbl_data.synonyms:
                table_synonym_map[synonym] = tbl_name

        # Synonym match
        if table_name in table_synonym_map:
            return table_synonym_map[table_name]

        # Fuzzy match
        best_match = difflib.get_close_matches(table_name, table_candidates, n=1, cutoff=0.7)
        return best_match[0] if best_match else None

    @staticmethod
    def find_best_match_column_using_synonyms(table_name: str, column_name: str, schema: Schema) -> Optional[str]:
        """
        Find the closest matching column name for a given table using synonyms and fuzzy matching.
        Returns 'table.column' or None if no match is found.
        """

        if table_name not in schema.tables:
            return None

        table = schema.tables[table_name]
        column_candidates = list(table.columns.keys())

        # Check synonyms for exact match
        for col_name, col_data in table.columns.items():
            if column_name in col_data.synonyms:
                return f"{table_name}.{col_name}"

        # Fuzzy match
        best_match = difflib.get_close_matches(column_name, column_candidates, n=1, cutoff=0.7)
        return f"{table_name}.{best_match[0]}" if best_match else None


    @staticmethod
    def expand_wildcard_columns(
        table_name: str,
        schema: Schema,
        remove_sensitive: bool = False
    ) -> List[str]:
        """
        Return a list of columns for the given table, expanding '*' and optionally excluding
        sensitive columns if 'remove_sensitive' is True.
        """
        if table_name not in schema.tables:
            return []

        expanded_cols = []
        for col_name, col_data in schema.tables[table_name].columns.items():
            if remove_sensitive and col_data.is_sensitive_column:
                continue
            expanded_cols.append(f"{table_name}.{col_name}")

        return expanded_cols