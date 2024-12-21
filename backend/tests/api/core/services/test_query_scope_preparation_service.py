import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from model.query_scope import QueryScope, Entities
from model.responses.schema.schema_tables_response import SchemaTablesResponse, TableResponse
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.validate_query_scope_utils import ValidateQueryScopeUtils
from api.core.services.query_scope.query_scope_preparation_service import QueryScopePreparationService 

class TestQueryScopePreparationService:

    @mock.patch.object(SchemaManagerService, 'get_schema_tables', new_callable=AsyncMock)
    @mock.patch.object(ValidateQueryScopeUtils, 'validate_tables_exist_in_schemas')
    @pytest.mark.asyncio
    async def test_prepare_query_scope_success(self, mock_validate_tables_exist, mock_get_schema_tables):
        # Arrange
        tenant_id = 'tenant123'
        
        mock_schema = MagicMock(spec=SchemaTablesResponse)
        mock_schema.schema_name = 'public'
        mock_table_users = MagicMock(spec=TableResponse)
        mock_table_users.table_name = 'users'
        mock_table_users.columns = []
        mock_table_orders = MagicMock(spec=TableResponse)
        mock_table_orders.table_name = 'orders'
        mock_table_orders.columns = []
        mock_schema.tables = [mock_table_users, mock_table_orders]
        
        mock_get_schema_tables.return_value = [mock_schema]
        mock_validate_tables_exist.return_value = True

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['user', 'order'],
                columns=['user.id', 'order.amount']
            )
        )

        # Act
        schemas = await QueryScopePreparationService.prepare_query_scope(tenant_id, query_scope)

        # Assert
        mock_get_schema_tables.assert_awaited_once_with(tenant_id=tenant_id)
        mock_validate_tables_exist.assert_called_once_with([mock_schema], query_scope)

        assert schemas == [mock_schema]
        assert query_scope.entities.tables == ['users', 'orders']
        assert query_scope.entities.columns == ['users.id', 'orders.amount']

    @mock.patch.object(SchemaManagerService, 'get_schema_tables', new_callable=AsyncMock)
    @mock.patch.object(ValidateQueryScopeUtils, 'validate_tables_exist_in_schemas')
    @pytest.mark.asyncio
    async def test_prepare_query_scope_tables_do_not_exist(self, mock_validate_tables_exist, mock_get_schema_tables):
        # Arrange
        tenant_id = 'tenant123'
        
        mock_schema = MagicMock(spec=SchemaTablesResponse)
        mock_schema.schema_name = 'public'
        mock_table_users = MagicMock(spec=TableResponse)
        mock_table_users.table_name = 'users'
        mock_table_users.columns = []
        mock_table_orders = MagicMock(spec=TableResponse)
        mock_table_orders.table_name = 'orders'
        mock_table_orders.columns = []
        mock_schema.tables = [mock_table_users, mock_table_orders]
        
        mock_get_schema_tables.return_value = [mock_schema]
        mock_validate_tables_exist.return_value = False

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['nonexistent_table'],
                columns=['nonexistent_table.id']
            )
        )

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await QueryScopePreparationService.prepare_query_scope(tenant_id, query_scope)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "One or more tables in the user request do not exist in the schemas."

        # Assert
        mock_get_schema_tables.assert_awaited_once_with(tenant_id=tenant_id)
        mock_validate_tables_exist.assert_called_once_with([mock_schema], query_scope)

    @mock.patch.object(SchemaManagerService, 'get_schema_tables', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_prepare_query_scope_invalid_schema_object(self, mock_get_schema_tables):
        # Arrange
        tenant_id = 'tenant123'
        
        mock_invalid_schema = MagicMock()
        mock_invalid_schema.tables = [MagicMock(table_name='users')]
        
        mock_get_schema_tables.return_value = [mock_invalid_schema]

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['user'],
                columns=['user.id']
            )
        )

        # Act
        with pytest.raises(AttributeError) as exc_info:
            await QueryScopePreparationService.prepare_query_scope(tenant_id, query_scope)
        
        assert "Expected SchemaTablesResponse object, but got" in str(exc_info.value)

        # Assert
        mock_get_schema_tables.assert_awaited_once_with(tenant_id=tenant_id)

    @mock.patch.object(SchemaManagerService, 'get_schema_tables', new_callable=AsyncMock)
    @mock.patch.object(ValidateQueryScopeUtils, 'validate_tables_exist_in_schemas')
    @pytest.mark.asyncio
    async def test_prepare_query_scope_no_soft_preprocessing_needed(self, mock_validate_tables_exist, mock_get_schema_tables):
        # Arrange
        tenant_id = 'tenant123'
        
        mock_schema = MagicMock(spec=SchemaTablesResponse)
        mock_schema.schema_name = 'public'
        mock_table_users = MagicMock(spec=TableResponse)
        mock_table_users.table_name = 'users'
        mock_table_users.columns = []
        mock_table_orders = MagicMock(spec=TableResponse)
        mock_table_orders.table_name = 'orders'
        mock_table_orders.columns = []
        mock_schema.tables = [mock_table_users, mock_table_orders]
        
        mock_get_schema_tables.return_value = [mock_schema]
        mock_validate_tables_exist.return_value = True

        query_scope = QueryScope(
            intent='test_intent',
            entities=Entities(
                tables=['users', 'orders'],
                columns=['users.id', 'orders.amount']
            )
        )

        # Act
        schemas = await QueryScopePreparationService.prepare_query_scope(tenant_id, query_scope)

        # Assert
        mock_get_schema_tables.assert_awaited_once_with(tenant_id=tenant_id)
        mock_validate_tables_exist.assert_called_once_with([mock_schema], query_scope)

        assert schemas == [mock_schema]
        assert query_scope.entities.tables == ['users', 'orders']
        assert query_scope.entities.columns == ['users.id', 'orders.amount']

    @mock.patch.object(SchemaManagerService, 'get_schema_tables', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_prepare_query_scope_multiple_corrections_success(self, mock_get_schema_tables):
        # Arrange
        tenant_id = 'tenant123'
        
        mock_schema = MagicMock(spec=SchemaTablesResponse)
        mock_schema.schema_name = 'public'
        mock_table_users = MagicMock(spec=TableResponse)
        mock_table_users.table_name = 'users'
        mock_table_users.columns = []
        mock_table_orders = MagicMock(spec=TableResponse)
        mock_table_orders.table_name = 'orders'
        mock_table_orders.columns = []
        mock_table_products = MagicMock(spec=TableResponse)
        mock_table_products.table_name = 'products'
        mock_table_products.columns = []
        mock_schema.tables = [mock_table_users, mock_table_orders, mock_table_products]
        
        mock_get_schema_tables.return_value = [mock_schema]

        with mock.patch.object(ValidateQueryScopeUtils, 'validate_tables_exist_in_schemas') as mock_validate:
            mock_validate.return_value = True

            query_scope = QueryScope(
                intent='test_intent',
                entities=Entities(
                    tables=['user', 'order', 'product'],
                    columns=['user.id', 'order.amount', 'product.price']
                )
            )

            # Act
            schemas_returned = await QueryScopePreparationService.prepare_query_scope(tenant_id, query_scope)

            # Assert
            mock_get_schema_tables.assert_awaited_once_with(tenant_id=tenant_id)
            mock_validate.assert_called_once_with([mock_schema], query_scope)

            assert schemas_returned == [mock_schema]
            assert query_scope.entities.tables == ['users', 'orders', 'products']
            assert query_scope.entities.columns == ['users.id', 'orders.amount', 'products.price']

    @mock.patch.object(SchemaManagerService, 'get_schema_tables', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_prepare_query_scope_multiple_corrections_failure(self, mock_get_schema_tables):
        # Arrange
        tenant_id = 'tenant123'
        
        mock_schema = MagicMock(spec=SchemaTablesResponse)
        mock_schema.schema_name = 'public'
        mock_table_users = MagicMock(spec=TableResponse)
        mock_table_users.table_name = 'users'
        mock_table_users.columns = []
        mock_table_orders = MagicMock(spec=TableResponse)
        mock_table_orders.table_name = 'orders'
        mock_table_orders.columns = []
        mock_schema.tables = [mock_table_users, mock_table_orders]
        
        mock_get_schema_tables.return_value = [mock_schema]

        with mock.patch.object(ValidateQueryScopeUtils, 'validate_tables_exist_in_schemas') as mock_validate:
            mock_validate.return_value = False

            query_scope = QueryScope(
                intent='test_intent',
                entities=Entities(
                    tables=['user', 'order', 'product'],
                    columns=['user.id', 'order.amount', 'product.price']
                )
            )

            # Act
            with pytest.raises(HTTPException) as exc_info:
                await QueryScopePreparationService.prepare_query_scope(tenant_id, query_scope)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "One or more tables in the user request do not exist in the schemas."

            # ssert
            mock_get_schema_tables.assert_awaited_once_with(tenant_id=tenant_id)
            mock_validate.assert_called_once_with([mock_schema], query_scope)
