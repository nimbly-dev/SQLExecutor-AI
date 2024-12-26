
import logging
from typing import List, Dict, Any, Union
from fastapi import HTTPException

from model.authentication.external_user_session_data import ExternalSessionData
from model.query_scope.query_scope import QueryScope
from model.schema.schema import Schema
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.services.query_scope.query_scope_preparation_service import QueryScopePreparationService
from api.core.services.query_scope.query_scope_resolution_service import QueryScopeResolutionService
from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY

logger = logging.getLogger(__name__)

class QueryScopeResolver:
    """
    Entrypoint for resolving the QueryScope output from the LLM model.
    Utilizes two consolidated services:
        - QueryScopePreparationService
        - QueryScopeResolutionService
    to handle schema fetching, soft preprocessing, matching, and final processing.
    """

    def __init__(self, session_data: ExternalSessionData, settings: Dict[str, Any], query_scope: QueryScope):
        self.session_data = session_data
        self.settings = settings or {}
        self.query_scope = query_scope
        self.schemas = []

    async def match_user_query_to_schema(self, tenant_id: str) -> Union[Dict[str, List[str]], Any]:
        """
        Fetch and validate schemas, then match the query scope to the most relevant
        schema(s) and return the appropriate response.
        """
        # Fetch and preprocess
        self.schemas = await QueryScopePreparationService.prepare_query_scope(
            tenant_id=tenant_id,
            query_scope=self.query_scope
        )

        # Match best schema
        tenant_settings = {
            "IGNORE_COLUMN_WILDCARDS": SettingUtils.get_setting_value(
                settings=self.settings,
                category_key=POST_PROCESS_QUERYSCOPE_CATEGORY_KEY,
                setting_key="IGNORE_COLUMN_WILDCARDS"
            )
        }
        return await QueryScopeResolutionService.match_schema(
            tenant_id=tenant_id,
            schemas=self.schemas,
            query_scope=self.query_scope,
            tenant_settings=tenant_settings
        )

    def resolve_query_scope(self, matched_schema: Schema) -> QueryScope:
        """
        Perform final processing of the QueryScope using the matched schema.
        """
        return QueryScopeResolutionService.process_query_scope(
            matched_schema=matched_schema,
            query_scope=self.query_scope,
            session_data=self.session_data,
            settings=self.settings
        )