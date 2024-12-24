import pytest
from unittest import mock
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from model.schema.schema import Schema
from model.schema.column import Column
from model.schema.joins import Joins
from model.schema.table import Table
from model.tenant.tenant import Tenant
from model.requests.schema_manager.add_schema_request import AddSchemaRequest
from model.requests.schema_manager.update_schema_request import UpdateSchemaRequest
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.database import mongodb

class TestSchemaManagerService:

    def init_mock_tenant(self, tenant_id):
        return {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant"
        }

    def init_mock_schema_request(self):
        return AddSchemaRequest(
            schema_name="new_schema",
            description="Test schema",
            tables={},
            filter_rules=[],
            exclude_description_on_generate_sql=False
        )

    def init_mock_schema_data(self):
        return {
            "tenant_id": "tenant1",
            "schema_name": "new_schema",
            "description": "Test schema",
            "tables": {},
            "filter_rules": [],
            "exclude_description_on_generate_sql": False,
            "synonyms": None
        }

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_add_schema_success(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_request = self.init_mock_schema_request()
        tenant_dict = self.init_mock_tenant(tenant_id)

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
            "exclude_description_on_generate_sql": False,
            "synonyms": None
        })
        assert result == {"message": "Schema added successfully", "schema_id": "123"}

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_add_schema_tenant_not_found(self, mock_db):
        # Arrange
        tenant_id = "nonexistent_tenant"
        schema_request = self.init_mock_schema_request()

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

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_add_schema_duplicate_schema(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_request = self.init_mock_schema_request()
        tenant_dict = self.init_mock_tenant(tenant_id)

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

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_get_schema_success(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_name = "new_schema"
        schema_data = self.init_mock_schema_data()

        mock_collection_schema = mock.AsyncMock()
        mock_collection_schema.find_one.return_value = schema_data
        mock_db.__getitem__.side_effect = lambda key: mock_collection_schema if key == "schemas" else None

        # Act
        result = await SchemaManagerService.get_schema(tenant_id, schema_name)

        # Assert
        mock_collection_schema.find_one.assert_called_once_with({"tenant_id": tenant_id, "schema_name": schema_name})
        assert result == Schema(**schema_data)

    @pytest.mark.asyncio
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

    @pytest.mark.skip(reason="SQLEXEC-44: Fix UT for test_get_schemas_success in TestSchemaManagerService")
    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_get_schemas_success(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_data = [self.init_mock_schema_data()]

        mock_collection_schema = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection_schema if key == "schemas" else None

        mock_cursor = mock.AsyncMock()
        mock_cursor.__aiter__.return_value = schema_data  # Async iterator for schema data
        mock_collection_schema.find.return_value = mock_cursor  # Return async cursor

        # Act
        result = await SchemaManagerService.get_schemas(tenant_id)

        # Assert
        assert len(result) == 1
        assert result[0] == Schema(**schema_data[0])

        
    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_delete_schema_success(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_name = "new_schema"

        mock_collection_schema = mock.AsyncMock()
        mock_collection_schema.delete_one.return_value.deleted_count = 1
        mock_db.__getitem__.side_effect = lambda key: mock_collection_schema if key == "schemas" else None

        # Act
        result = await SchemaManagerService.delete_schema(tenant_id, schema_name)

        # Assert
        assert result == {"message": "Schema deleted successfully"}

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_delete_schema_not_found(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        schema_name = "non_existing_schema"

        mock_collection_schema = mock.AsyncMock()
        mock_collection_schema.delete_one.return_value.deleted_count = 0
        mock_db.__getitem__.side_effect = lambda key: mock_collection_schema if key == "schemas" else None

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await SchemaManagerService.delete_schema(tenant_id, schema_name)

        # Assert
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Schema not found"
