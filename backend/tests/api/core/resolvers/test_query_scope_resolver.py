import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from api.core.resolvers.query_scope.query_scope_resolver import QueryScopeResolver
from model.authentication.external_user_session_data import ExternalSessionData
from model.query_scope.query_scope import QueryScope, Entities
from model.schema.schema import Schema
from model.tenant.setting import Setting
from model.tenant.tenant import Tenant

class TestQueryScopeResolver:
    """
    Unit tests for the QueryScopeResolver class.
    """

    @pytest.fixture
    def sample_session_data(self):
        return ExternalSessionData(
            session_id="509e74ba-8d1f-4ab9-9eb0-91648debd095",
            tenant_id="TENANT_TST2",
            user_id="test_user",
            custom_fields={
                "roles": ["user"],
                "active": True,
                "preferences": {
                    "vip": False,
                    "notifications": True
                },
                "permissions": ["read_only"],
                "otherField": "test_value"
            },
            created_at="2024-12-21T11:08:40.925734+00:00",
            expires_at="2024-12-21T11:23:40+00:00",
            session_settings={
                "SQL_GENERATION": {
                    "REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": Setting(
                        setting_description="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE description not provided",
                        setting_basic_name="Remove Missing Columns on query scope",
                        setting_default_value="true",
                        setting_value="true",
                        is_custom_setting=False
                    ),
                    "IGNORE_COLUMN_WILDCARDS": Setting(
                        setting_description="IGNORE_COLUMN_WILDCARDS description not provided",
                        setting_basic_name="Ignore Column Wildcards",
                        setting_default_value="true",
                        setting_value="true",
                        is_custom_setting=False
                    )
                }
            }
        )

    @pytest.fixture
    def sample_query_scope(self):
        return QueryScope(
            intent="test_intent",
            entities=Entities(
                tables=["users", "orders"],
                columns=["users.id", "users.password", "orders.amount"]
            )
        )

    @pytest.fixture
    def sample_settings(self):
        return {
            "POST_PROCESS_QUERYSCOPE": {
                "REMOVE_SENSITIVE_COLUMNS": Setting(
                    setting_description="Removes sensitive columns that were declared on schema",
                    setting_basic_name="Remove sensitive columns",
                    setting_default_value="true",
                    setting_value="true",
                    is_custom_setting=False
                ),
                "IGNORE_COLUMN_WILDCARDS": Setting(
                    setting_description="IGNORE_COLUMN_WILDCARDS description not provided",
                    setting_basic_name="Ignore Column Wildcards",
                    setting_default_value="true",
                    setting_value="true",
                    is_custom_setting=False
                )
            }
        }

    @mock.patch('api.core.services.query_scope.query_scope_preparation_service.QueryScopePreparationService.prepare_query_scope', new_callable=AsyncMock)
    @mock.patch('api.core.services.query_scope.query_scope_resolution_service.QueryScopeResolutionService.match_schema', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_match_user_query_to_schema_success(
        self,
        mock_match_schema,
        mock_prepare_query_scope,
        sample_session_data,
        sample_query_scope,
        sample_settings
    ):
        # Arrange
        tenant_id = sample_session_data.tenant_id

        mock_schema = MagicMock(spec=Schema, schema_name="public")
        mock_tenant = MagicMock(spec=Tenant, tenant_name="TST123")
        mock_prepare_query_scope.return_value = [mock_schema]
        mock_match_schema.return_value = mock_schema

        resolver = QueryScopeResolver(
            session_data=sample_session_data,
            settings=sample_settings,
            query_scope=sample_query_scope,
            tenant=mock_tenant
        )

        # Act
        result = await resolver.match_user_query_to_schema(tenant_id=tenant_id)

        # Assert
        mock_prepare_query_scope.assert_awaited_once_with(
            tenant_id=tenant_id,
            query_scope=sample_query_scope
        )
        mock_match_schema.assert_awaited_once_with(
            tenant_id=tenant_id,
            schemas=[mock_schema],
            query_scope=sample_query_scope,
            tenant_settings={
                "IGNORE_COLUMN_WILDCARDS": True  
            }
        )
        assert result == mock_schema


    @mock.patch('api.core.services.query_scope.query_scope_preparation_service.QueryScopePreparationService.prepare_query_scope', new_callable=AsyncMock)
    @mock.patch('api.core.services.query_scope.query_scope_resolution_service.QueryScopeResolutionService.match_schema', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_match_user_query_to_schema_preparation_failure(
        self,
        mock_match_schema,
        mock_prepare_query_scope,
        sample_session_data,
        sample_query_scope,
        sample_settings
    ):
        # Arrange
        tenant_id = sample_session_data.tenant_id

        mock_prepare_query_scope.side_effect = HTTPException(status_code=500, detail="Preparation failed.")
        mock_tenant = MagicMock(spec=Tenant, tenant_name="TST123")
        resolver = QueryScopeResolver(
            session_data=sample_session_data,
            settings=sample_settings,
            query_scope=sample_query_scope,
            tenant=mock_tenant
        )

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await resolver.match_user_query_to_schema(tenant_id=tenant_id)

        
        # Assert
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Preparation failed."

        mock_prepare_query_scope.assert_awaited_once_with(
            tenant_id=tenant_id,
            query_scope=sample_query_scope
        )
        mock_match_schema.assert_not_called()

    @mock.patch('api.core.services.query_scope.query_scope_preparation_service.QueryScopePreparationService.prepare_query_scope', new_callable=AsyncMock)
    @mock.patch('api.core.services.query_scope.query_scope_resolution_service.QueryScopeResolutionService.match_schema', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_match_user_query_to_schema_matching_failure(
        self,
        mock_match_schema,
        mock_prepare_query_scope,
        sample_session_data,
        sample_query_scope,
        sample_settings
    ):
        # Arrange
        tenant_id = sample_session_data.tenant_id

        mock_schema = MagicMock(spec=Schema, schema_name="public")
        mock_tenant = MagicMock(spec=Tenant, tenant_name="TST123")
        mock_prepare_query_scope.return_value = [mock_schema]
        mock_match_schema.side_effect = HTTPException(status_code=400, detail="Matching failed.")

        resolver = QueryScopeResolver(
            session_data=sample_session_data,
            settings=sample_settings,
            query_scope=sample_query_scope,
            tenant=mock_tenant
        )

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await resolver.match_user_query_to_schema(tenant_id=tenant_id)

        # Assert
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Matching failed."

        mock_prepare_query_scope.assert_awaited_once_with(
            tenant_id=tenant_id,
            query_scope=sample_query_scope
        )
        mock_match_schema.assert_awaited_once_with(
            tenant_id=tenant_id,
            schemas=[mock_schema],
            query_scope=sample_query_scope,
            tenant_settings={
                "IGNORE_COLUMN_WILDCARDS": True
            }
        )

    @mock.patch('api.core.services.query_scope.query_scope_resolution_service.QueryScopeResolutionService.process_query_scope', return_value=MagicMock(spec=QueryScope))
    def test_resolve_query_scope_success(
        self,
        mock_process_query_scope,
        sample_session_data,
        sample_query_scope,
        sample_settings
    ):
        # Arrange
        matched_schema = MagicMock(spec=Schema, schema_name="public")
        mock_tenant = MagicMock(spec=Tenant, tenant_name="TENANT_TST2")
        resolver = QueryScopeResolver(
            session_data=sample_session_data,
            settings=sample_settings,
            query_scope=sample_query_scope,
            tenant=mock_tenant
        )

        # Act
        result = resolver.resolve_query_scope(matched_schema=matched_schema)

        # Assert
        mock_process_query_scope.assert_called_once_with(
            matched_schema=matched_schema,
            query_scope=sample_query_scope,
            session_data=sample_session_data,
            settings=sample_settings,
            tenant=mock_tenant
        )
        assert result is not None  

    @mock.patch('api.core.services.query_scope.query_scope_resolution_service.QueryScopeResolutionService.process_query_scope', side_effect=HTTPException(
        status_code=400,
        detail={
            "message": "No valid columns remain after processing the input query.",
            "matched_schema": "public",
            "missing_columns": []
        }
    ))
    def test_resolve_query_scope_processing_failure(
        self,
        mock_process_query_scope,
        sample_session_data,
        sample_query_scope,
        sample_settings
    ):
        # Arrange
        matched_schema = MagicMock(spec=Schema, schema_name="public")
        mock_tenant = MagicMock(spec=Tenant, tenant_name="TENANT_TST2")
        resolver = QueryScopeResolver(
            session_data=sample_session_data,
            settings=sample_settings,
            query_scope=sample_query_scope,
            tenant=mock_tenant
        )

        # Act
        with pytest.raises(HTTPException) as exc_info:
            resolver.resolve_query_scope(matched_schema=matched_schema)

        # Assert
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["message"] == "No valid columns remain after processing the input query."
        assert exc_info.value.detail["matched_schema"] == "public"
        assert exc_info.value.detail["missing_columns"] == []

        mock_process_query_scope.assert_called_once_with(
            matched_schema=matched_schema,
            query_scope=sample_query_scope,
            session_data=sample_session_data,
            settings=sample_settings,
            tenant=mock_tenant
        )
