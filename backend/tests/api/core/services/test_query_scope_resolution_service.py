import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from model.authentication.external_user_session_data import ExternalSessionData
from model.query_scope.query_scope import QueryScope
from model.query_scope.entities import Entities
from model.schema.schema import Schema
from model.responses.schema.schema_tables_response import SchemaTablesResponse, TableResponse
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.post_process_query_scope_settings_utils import PostProcessQueryScopeSettingsUtils
from utils.query_scope.query_scope_utils import expand_columns
from utils.tenant_manager.setting_utils import SettingUtils
from utils.session.session_utils import get_session_setting
from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY
from api.core.services.query_scope.query_scope_resolution_service import QueryScopeResolutionService


class TestQueryScopeResolutionService:

    # Tests for match_schema method

    @mock.patch.object(SchemaDiscoveryService, 'get_best_matching_schemas', return_value='public')
    @mock.patch.object(SchemaManagerService, 'get_schema', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_match_schema_single_string_match(
        self,
        mock_get_schema,
        mock_get_best_matching_schemas
    ):
        # Arrange
        tenant_id = 'tenant123'
        matched_schema_name = 'public'

        mock_schema = MagicMock(spec=Schema)
        mock_schema.schema_name = matched_schema_name
        mock_get_schema.return_value = mock_schema

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['users'],
                columns=['users.id']
            )
        )

        # Act
        result = await QueryScopeResolutionService.match_schema(
            tenant_id=tenant_id,
            schemas=[],
            query_scope=query_scope,
            tenant_settings={}
        )

        # Assert
        mock_get_best_matching_schemas.assert_called_once_with(
            query_scope=query_scope,
            schemas=[],
            tenant_settings={}
        )
        mock_get_schema.assert_awaited_once_with(
            tenant_id=tenant_id,
            schema_name=matched_schema_name
        )
        assert result == mock_schema

    @mock.patch.object(SchemaDiscoveryService, 'get_best_matching_schemas', return_value=['sales'])
    @mock.patch.object(SchemaManagerService, 'get_schema', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_match_schema_single_list_match(
        self,
        mock_get_schema,
        mock_get_best_matching_schemas
    ):
        # Arrange
        tenant_id = 'tenant123'
        matched_schema_list = ['sales']

        mock_schema = MagicMock(spec=Schema)
        mock_schema.schema_name = 'sales'
        mock_get_schema.return_value = mock_schema

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['sales'],
                columns=['sales.revenue']
            )
        )

        # Act
        result = await QueryScopeResolutionService.match_schema(
            tenant_id=tenant_id,
            schemas=[],
            query_scope=query_scope,
            tenant_settings={}
        )

        # Assert
        mock_get_best_matching_schemas.assert_called_once_with(
            query_scope=query_scope,
            schemas=[],
            tenant_settings={}
        )
        mock_get_schema.assert_awaited_once_with(
            tenant_id=tenant_id,
            schema_name='sales'
        )
        assert result == mock_schema

    @mock.patch.object(SchemaDiscoveryService, 'get_best_matching_schemas', return_value=['public', 'sales'])
    @pytest.mark.asyncio
    async def test_match_schema_multiple_matches(
        self,
        mock_get_best_matching_schemas
    ):
        # Arrange
        tenant_id = 'tenant123'
        matched_schema_list = ['public', 'sales']

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['users', 'sales'],
                columns=['users.id', 'sales.revenue']
            )
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await QueryScopeResolutionService.match_schema(
                tenant_id=tenant_id,
                schemas=[],
                query_scope=query_scope,
                tenant_settings={}
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Multiple Schemas matched, SQLExecutor does not currently support this"

        mock_get_best_matching_schemas.assert_called_once_with(
            query_scope=query_scope,
            schemas=[],
            tenant_settings={}
        )

    @mock.patch.object(SchemaDiscoveryService, 'get_best_matching_schemas', return_value=[])
    @pytest.mark.asyncio
    async def test_match_schema_no_matches(
        self,
        mock_get_best_matching_schemas
    ):
        # Arrange
        tenant_id = 'tenant123'
        matched_result = []

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['unknown'],
                columns=['unknown.id']
            )
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await QueryScopeResolutionService.match_schema(
                tenant_id=tenant_id,
                schemas=[],
                query_scope=query_scope,
                tenant_settings={}
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "No matching schemas found."

        mock_get_best_matching_schemas.assert_called_once_with(
            query_scope=query_scope,
            schemas=[],
            tenant_settings={}
        )