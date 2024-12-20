import logging
from typing import List, Dict, Any, Union
from fastapi import HTTPException

from utils.database import mongodb
from model.session_data import SessionData
from model.query_scope import QueryScope
from model.schema import Schema
from model.responses.schema.schema_tables_response import SchemaTablesResponse
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.validate_query_scope_utils import ValidateQueryScopeUtils
from utils.query_scope.post_process_query_scope_settings_utils import PostProcessQueryScopeSettingsUtils
from utils.query_scope.query_scope_utils import expand_columns

class QueryScopeResolver:
    """
    Resolve the QueryScope output of the LLMModel, post-processing query scope.
    """

    def __init__(self, session_data: SessionData, settings: Dict[str, Any], query_scope: QueryScope):
        """
        Initialize QueryScopeResolver with session data, tenant settings, and the query scope.
        
        :param session_data: User-specific session data (e.g., JWT claims).
        :param settings: Tenant application settings.
        :param query_scope: Parsed query scope to be resolved.
        """
        self.session_data = session_data
        self.settings = settings or {} 
        self.query_scope = query_scope
        self.schemas = []
        

    async def match_user_query_to_schema(self, tenant_id: str) -> Union[Dict[str, List[str]], Any]:
        """
        Match the query scope to the most relevant schema(s) and return the appropriate response.
        
        :param tenant_id: The tenant ID for schema retrieval.
        :return: A single Schema object for one match, or a dictionary of schema names for multiple matches.
        """
        await self._fetch_and_validate_schemas(tenant_id)
        return await self._resolve_matched_schema(tenant_id)
    
    def resolve_query_scope(self, matched_schema: Schema) -> QueryScope:
        REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE = self._get_setting_toggle(setting_key="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE")
        IGNORE_COLUMN_WILDCARDS = self._get_setting_toggle(setting_key="IGNORE_COLUMN_WILDCARDS")

        missing_columns = []

        if REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE:
            self.query_scope, missing_columns = PostProcessQueryScopeSettingsUtils.remove_missing_columns_from_query_scope(
                matched_schema, query_scope=self.query_scope
            )
        
        if not IGNORE_COLUMN_WILDCARDS:
            schema_tables = {table_name for table_name in matched_schema.tables.keys()}
            schema_columns = {
                table_name: [column_name for column_name in table.columns.keys()]
                for table_name, table in matched_schema.tables.items()
            }
            
            expanded_columns = expand_columns(
                query_columns=set(self.query_scope.entities.columns),
                schema_tables=schema_tables,
                schema_columns=schema_columns
            )

            self.query_scope.entities.columns = list(expanded_columns)
        else:
            filtered_columns = [
                column for column in self.query_scope.entities.columns if not column.endswith(".*")
            ]
            self.query_scope.entities.columns = filtered_columns

        if not self.query_scope.entities.columns:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "No valid columns remain after processing the input query. The requested columns do not match the schema.",
                    "matched_schema": f"{matched_schema.schema_name}",
                    "missing_columns": missing_columns
                }
            )
            
        return self.query_scope

    async def _fetch_and_validate_schemas(self, tenant_id: str) -> None:
        """
        Fetch schemas for the tenant and validate if query scope tables exist.
        
        :param tenant_id: The tenant ID for schema retrieval.
        """
        schemas = await SchemaManagerService.get_schema_tables(tenant_id=tenant_id)
        self.schemas = schemas

        # Soft preprocess table names in the query scope
        self._soft_preprocess_tables()

        tables_exist = ValidateQueryScopeUtils.validate_tables_exist_in_schemas(
            schemas, self.query_scope
        )

        if not tables_exist:
            raise HTTPException(
                status_code=400,
                detail="One or more tables in the user request do not exist in the schemas."
            )

    async def _resolve_matched_schema(self, tenant_id: str) -> Union[Dict[str, List[str]], Any]:
        """
        Match query scope to schemas and resolve the best match.

        :param tenant_id: The tenant ID for schema retrieval.
        :return: A single Schema object for one match, or a dictionary of schema names for multiple matches.
        """
        matched_result = SchemaDiscoveryService.get_best_matching_schemas(
            query_scope=self.query_scope,
            schemas=self.schemas,
            tenant_settings={"IGNORE_COLUMN_WILDCARDS": self._get_setting_toggle(setting_key="IGNORE_COLUMN_WILDCARDS")}
        )

        # Handle single string match or list with one match
        if isinstance(matched_result, str):
            return await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=matched_result)
        if isinstance(matched_result, list) and len(matched_result) == 1:
            return await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=matched_result[0])

        if isinstance(matched_result, list) and len(matched_result) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple Schemas matched, SQLExecutor does not currently support this"
            )
            
        # Multiple Rulesets not supported in this PoC
        if len(self.schema.filter_rules) > 1:
            raise HTTPException(
                status_code=400,
                detail=f"Multiple rulesets found in schema '{self.schema.schema_name}'. "
                    "SQLExecutor does not currently support multiple rulesets."
            )

        # Handle no matches
        raise HTTPException(status_code=404, detail="No matching schemas found.")

    
    def _get_setting_toggle(self, setting_key:str) -> bool:
        setting = self.settings.get(setting_key)
        if setting and hasattr(setting, "setting_value"):
            value = str(setting.setting_value).strip().lower()
            # Explicitly check for truthy values
            if value in {"true", "1", "yes", "on"}:
                return True
            elif value in {"false", "0", "no", "off"}:
                return False
        return False
        
    def _soft_preprocess_tables(self):
        """
        Soft pre-process table names and associated column names in the query scope
        by correcting minor errors (e.g., missing 's').
        """
        # Extract valid table names from the schemas
        valid_tables = set()

        for schema in self.schemas:
            if isinstance(schema, SchemaTablesResponse):  # Ensure the object is SchemaTablesResponse
                # Extract table names from the list of TableResponse objects
                valid_tables.update(table.table_name for table in schema.tables)
            else:
                raise AttributeError(f"Expected SchemaTablesResponse object, but got {type(schema)}")

        # Debug: Print valid table names
        print(f"Valid tables: {valid_tables}")

        # Preprocess table names in the query scope
        corrected_tables = []
        table_name_mapping = {}  # To track corrections for columns
        for table in self.query_scope.entities.tables:
            if table in valid_tables:
                corrected_tables.append(table)  # Table is already valid
                table_name_mapping[table] = table
            elif table + "s" in valid_tables:  # Check for missing 's'
                corrected_name = table + "s"
                corrected_tables.append(corrected_name)
                table_name_mapping[table] = corrected_name
                print(f"Soft fix applied: '{table}' -> '{corrected_name}'")
            elif table[:-1] in valid_tables and table.endswith("s"):  # Check for extra 's'
                corrected_name = table[:-1]
                corrected_tables.append(corrected_name)
                table_name_mapping[table] = corrected_name
                print(f"Soft fix applied: '{table}' -> '{corrected_name}'")
            else:
                corrected_tables.append(table)  # Leave the table as-is if no match
                table_name_mapping[table] = table
                print(f"No soft fix applied for: '{table}'")

        # Debug: Print corrected tables
        print(f"Corrected tables: {corrected_tables}")

        # Update column names in the query scope based on corrected table names
        corrected_columns = []
        for column in self.query_scope.entities.columns:
            if "." in column:
                table_name, column_name = column.split(".", 1)
                corrected_table_name = table_name_mapping.get(table_name, table_name)
                corrected_columns.append(f"{corrected_table_name}.{column_name}")
            else:
                corrected_columns.append(column)

        # Debug: Print corrected columns
        print(f"Corrected columns: {corrected_columns}")

        # Update the query scope with corrected table and column names
        self.query_scope.entities.tables = corrected_tables
        self.query_scope.entities.columns = corrected_columns
