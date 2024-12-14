import pytest
from unittest import mock
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from model.session_data import SessionData
from model.query_scope import QueryScope, Entities
from model.responses.schema.schema_tables_response import SchemaTablesResponse, TableResponse
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.validate_query_scope_utils import ValidateQueryScopeUtils
from api.core.resolvers.query_scope.query_scope_resolver import QueryScopeResolver


class TestQueryScopeResolver:

    @pytest.fixture
    def session_data(self) -> SessionData:
        return SessionData(
            session_id=uuid.uuid4(),
            tenant_id="tenant1",
            user_id="user1",
            custom_fields={"roles": ["admin"]},
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )

    @pytest.fixture
    def query_scope(self) -> QueryScope:
        return QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["products", "orders"],
                columns=["products.product_id", "orders.order_id"]
            )
        )

    @pytest.fixture
    def settings(self) -> dict:
        return {"IGNORE_COLUMN_WILDCARDS": mock.Mock(setting_value=True)}

    @pytest.fixture
    def schemas(self) -> list:
        return [
            SchemaTablesResponse(
                schema_name="schema1",
                tables=[
                    TableResponse(table_name="products", columns=[]),
                    TableResponse(table_name="categories", columns=[])
                ]
            ),
            SchemaTablesResponse(
                schema_name="schema2",
                tables=[
                    TableResponse(table_name="orders", columns=[]),
                    TableResponse(table_name="customers", columns=[])
                ]
            )
        ]

    @pytest.mark.asyncio
    @mock.patch.object(SchemaManagerService, "get_schema_tables")
    @mock.patch.object(SchemaManagerService, "get_schema")
    @mock.patch.object(SchemaDiscoveryService, "get_best_matching_schemas")
    async def test_match_user_query_to_schema_single_match(
        self, mock_get_best_matching_schemas, mock_get_schema, mock_get_schema_tables, session_data, query_scope, settings, schemas
    ):
        # Arrange
        tenant_id = session_data.tenant_id

        mock_get_schema_tables.return_value = schemas
        mock_get_best_matching_schemas.return_value = "schema1"  
        mock_get_schema.return_value = schemas[0]

        resolver = QueryScopeResolver(session_data, settings, query_scope)

        # Act
        result = await resolver.match_user_query_to_schema(tenant_id)

        # Assert
        mock_get_schema_tables.assert_called_once_with(tenant_id=tenant_id)
        mock_get_best_matching_schemas.assert_called_once_with(
            query_scope=query_scope, schemas=schemas, tenant_settings={"IGNORE_COLUMN_WILDCARDS": True}
        )
        mock_get_schema.assert_called_once_with(tenant_id=tenant_id, schema_name="schema1")  
        assert result == schemas[0]



    @pytest.mark.asyncio
    @mock.patch.object(SchemaManagerService, "get_schema_tables")
    @mock.patch.object(SchemaDiscoveryService, "get_best_matching_schemas")
    async def test_match_user_query_to_schema_multiple_match_error(
        self, mock_get_best_matching_schemas, mock_get_schema_tables, session_data, query_scope, settings, schemas
    ):
        # Arrange
        tenant_id = session_data.tenant_id
        mock_get_schema_tables.return_value = schemas
        mock_get_best_matching_schemas.return_value = ["schema1", "schema2"]

        resolver = QueryScopeResolver(session_data, settings, query_scope)

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await resolver.match_user_query_to_schema(tenant_id)

        # Assert
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Multiple Schemas matched, SQLExecutor does not currently support this"

    @pytest.mark.asyncio
    @mock.patch.object(SchemaManagerService, "get_schema_tables")
    @mock.patch.object(SchemaDiscoveryService, "get_best_matching_schemas")
    async def test_match_user_query_to_schema_no_match_error(
        self, mock_get_best_matching_schemas, mock_get_schema_tables, session_data, query_scope, settings, schemas
    ):
        # Arrange
        tenant_id = session_data.tenant_id
        mock_get_schema_tables.return_value = schemas
        mock_get_best_matching_schemas.return_value = []

        resolver = QueryScopeResolver(session_data, settings, query_scope)

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await resolver.match_user_query_to_schema(tenant_id)

        # Assert
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "No matching schemas found."

    @pytest.mark.asyncio
    @mock.patch.object(SchemaManagerService, "get_schema_tables")
    @mock.patch.object(ValidateQueryScopeUtils, "validate_tables_exist_in_schemas")
    async def test_fetch_and_validate_schemas_table_not_found_error(
        self, mock_validate_tables_exist_in_schemas, mock_get_schema_tables, session_data, query_scope, settings, schemas
    ):
        # Arrange
        tenant_id = session_data.tenant_id
        mock_get_schema_tables.return_value = schemas
        mock_validate_tables_exist_in_schemas.return_value = False

        resolver = QueryScopeResolver(session_data, settings, query_scope)

        # Act 
        with pytest.raises(HTTPException) as exc_info:
            await resolver._fetch_and_validate_schemas(tenant_id)

        # Assert
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "One or more tables in the user request do not exist in the schemas."
