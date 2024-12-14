import logging
from typing import List, Dict, Any, Union
from fastapi import HTTPException

from utils.database import mongodb
from model.session_data import SessionData
from model.query_scope import QueryScope
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.validate_query_scope_utils import ValidateQueryScopeUtils

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

    async def _fetch_and_validate_schemas(self, tenant_id: str) -> None:
        """
        Fetch schemas for the tenant and validate if query scope tables exist.
        
        :param tenant_id: The tenant ID for schema retrieval.
        """
        schemas = await SchemaManagerService.get_schema_tables(tenant_id=tenant_id)
        self.schemas = schemas

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
            tenant_settings={"IGNORE_COLUMN_WILDCARDS": self._get_ignore_column_wildcards_setting()}
        )
        print(f"DEBUG: matched_result = {matched_result}")

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

        # Handle no matches
        raise HTTPException(status_code=404, detail="No matching schemas found.")


    def _get_ignore_column_wildcards_setting(self) -> bool:
        """
        Extract the IGNORE_COLUMN_WILDCARDS setting from tenant settings.
        
        :return: Boolean indicating whether column wildcards should be ignored.
        """
        setting = self.settings.get("IGNORE_COLUMN_WILDCARDS")
        if setting and hasattr(setting, "setting_value"):
            return setting.setting_value
        return False
