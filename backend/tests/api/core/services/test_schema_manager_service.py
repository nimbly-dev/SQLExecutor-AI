import pytest
from unittest import mock
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError 
from api.core.services.schema.schema_manager_service import SchemaManagerService
from model.responses.schema.schema_tables_response import SchemaTablesResponse, TableResponse, ColumnResponse
from model.requests.schema_manager.add_schema_request import AddSchemaRequest 
from model.requests.schema_manager.update_schema_request import UpdateSchemaRequest
from model.schema import Schema

from utils.database import mongodb

@pytest.mark.asyncio
class TestSchemaManagerService:
    
    @mock.patch("utils.database.mongodb.db")
    async def test_add_schema_success(self, mock_db):
        # Arrange
        schema_request = AddSchemaRequest(
            schema_name="new_schema",
            description="Test schema",
            tables={},
            filter_rules=[],
            exclude_description_on_generate_sql=False
        )

        tenant_id = "tenant1"
        tenant_dict = {"tenant_id": tenant_id, "tenant_name": "Test Tenant"}
        
        mock_collection_tenant = mock.AsyncMock()
        mock_collection_tenant.find_one.return_value = tenant_dict
        mock_collection_schema = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection_tenant if key == "tenants" else mock_collection_schema
        
        mock_collection_schema.insert_one.return_value = mock.Mock(inserted_id=123)

        # Act
        result = await SchemaManagerService.add_schema(tenant_id, schema_request)

        # Assert
        mock_collection_schema.insert_one.assert_called_once_with({
            "tenant_id": tenant_id,
            "schema_name": "new_schema",
            "description": "Test schema",
            "tables": {},
            "filter_rules": [],
            "exclude_description_on_generate_sql": False
        })
        assert result == {"message": "Schema added successfully", "schema_id": "123"}

    @mock.patch("utils.database.mongodb.db")
    async def test_add_schema_tenant_not_found(self, mock_db):
        # Arrange
        schema_request = AddSchemaRequest(
            schema_name="new_schema",
            description="Test schema",
            tables={},
            filter_rules=[],
            exclude_description_on_generate_sql=False
        )

        tenant_id = "nonexistent_tenant"
        mock_collection_tenant = mock.AsyncMock()
        mock_collection_tenant.find_one.return_value = None
        mock_collection_schema = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection_tenant if key == "tenants" else mock_collection_schema

        # Act 
        with pytest.raises(HTTPException) as exc_info:
            await SchemaManagerService.add_schema(tenant_id, schema_request)

        # Assert
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Tenant not found"

    @mock.patch("utils.database.mongodb.db")
    async def test_add_schema_duplicate_schema(self, mock_db):
        # Arrange
        schema_request = AddSchemaRequest(
            schema_name="new_schema",
            description="Test schema",
            tables={},
            filter_rules=[],
            exclude_description_on_generate_sql=False
        )

        tenant_id = "tenant1"
        tenant_dict = {"tenant_id": tenant_id, "tenant_name": "Test Tenant"}
        
        mock_collection_tenant = mock.AsyncMock()
        mock_collection_tenant.find_one.return_value = tenant_dict
        mock_collection_schema = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection_tenant if key == "tenants" else mock_collection_schema
        
        mock_collection_schema.insert_one.side_effect = DuplicateKeyError("Duplicate key error")

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await SchemaManagerService.add_schema(tenant_id, schema_request)

        # Assert
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Schema with the name 'new_schema' already exists for this tenant."

    @mock.patch("utils.database.mongodb.db")
    async def test_get_schema_success(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_name = "inventory_management"
        schema_data = {
            "tenant_id": tenant_id,
            "schema_name": schema_name,
            "description": "Schema for inventory management",
            "tables": {},
            "filter_rules": [],
            "exclude_description_on_generate_sql": False
        }
        
        mock_collection_schema = mock.AsyncMock()
        mock_collection_schema.find_one.return_value = schema_data
        mock_db.__getitem__.side_effect = lambda key: mock_collection_schema if key == "schemas" else None

        # Act
        result = await SchemaManagerService.get_schema(tenant_id, schema_name)

        # Assert
        mock_collection_schema.find_one.assert_called_once_with({"tenant_id": tenant_id, "schema_name": schema_name})
        assert result == Schema(**schema_data)

    @mock.patch("utils.database.mongodb.db")
    async def test_get_schema_not_found(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_name = "non_existing_schema"
        
        mock_collection_schema = mock.AsyncMock()
        mock_collection_schema.find_one.return_value = None
        mock_db.__getitem__.side_effect = lambda key: mock_collection_schema if key == "schemas" else None

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await SchemaManagerService.get_schema(tenant_id, schema_name)
        
        # Assert
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == f"No schema found with name '{schema_name}' for tenant '{tenant_id}'."
