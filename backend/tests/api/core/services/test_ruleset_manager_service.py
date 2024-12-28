import pytest
import json
from unittest import mock
from unittest.mock import AsyncMock
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from api.core.services.ruleset.ruleset_manager_service import RulesetManagerService
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest
from model.responses.ruleset_manager.ruleset_response import RulesetResponse
from model.ruleset.ruleset import Ruleset
from utils.database import mongodb
from model.tenant.tenant import Tenant
from pydantic import ValidationError
from tests.testing_utilities.test_utils import RESOURCES_PATH

@pytest.mark.asyncio
class TestRulesetManagerService:

    @mock.patch('utils.database.mongodb.db')
    async def test_create_indexes(self, mock_db):
        # Arrange
        mock_collection = mock.Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.create_index = mock.Mock()

        # Act
        await RulesetManagerService.create_indexes()

        # Assert
        mock_collection.create_index.assert_called_once_with([
            ("tenant_id", 1),
            ("ruleset_name", 1)
        ], unique=True)


    @mock.patch('api.core.services.ruleset.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_add_ruleset_success(self, mock_db, mock_get_tenant):
        # Arrange
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_tenant.return_value = Tenant(tenant_id="TENANT_123", tenant_name="Test Tenant")
        valid_request = AddRulesetRequest(**valid_json)

        expected_data = valid_request.dict()
        expected_data["tenant_id"] = "TENANT_123" 

        mock_collection.insert_one = AsyncMock(return_value=mock.Mock(inserted_id="mock_id"))

        # Act
        response = await RulesetManagerService.add_ruleset("TENANT_123", valid_request)

        # Assert
        mock_collection.insert_one.assert_called_once_with(expected_data)
        assert response == {"message": "Ruleset added successfully", "ruleset_id": "mock_id"}



    @mock.patch('api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_add_ruleset_duplicate_error(self, mock_db, mock_get_tenant):
        # Arrange
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_tenant.return_value = Tenant(tenant_id="tenant_123", tenant_name="Test Tenant")
        valid_request = AddRulesetRequest(**valid_json)
        mock_collection.insert_one.side_effect = DuplicateKeyError("Duplicate key error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await RulesetManagerService.add_ruleset("tenant_123", valid_request)

        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail

    @mock.patch('api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_get_ruleset_success(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "ecommerce_ruleset_with_user_specific_policy"
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        mock_get_tenant.return_value = Tenant(tenant_id=tenant_id, tenant_name="Test Tenant")
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        valid_json["tenant_id"] = tenant_id
        valid_json["ruleset_name"] = ruleset_name  # Ensure mock data matches the expected ruleset_name
        mock_collection.find_one = AsyncMock(return_value=valid_json)

        # Act
        response = await RulesetManagerService.get_ruleset(tenant_id, ruleset_name)

        # Assert
        assert response.ruleset_name == ruleset_name


    @mock.patch('api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_get_ruleset_not_found(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "non_existent_ruleset"
        mock_get_tenant.return_value = Tenant(tenant_id=tenant_id, tenant_name="Test Tenant")
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await RulesetManagerService.get_ruleset(tenant_id, ruleset_name)

        assert exc_info.value.status_code == 404
        assert "No Ruleset found" in exc_info.value.detail

    @mock.patch('api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_update_ruleset_success(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "ecommerce_ruleset"
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        update_request = AddRulesetRequest(**valid_json)
        mock_get_tenant.return_value = Tenant(tenant_id=tenant_id, tenant_name="Test Tenant")
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        
        # Ensure mock find_one returns all required fields
        mock_collection.find_one = AsyncMock(return_value={
            "tenant_id": tenant_id,
            "ruleset_name": ruleset_name,
            "description": "Sample ruleset description",
            "is_ruleset_enabled": True,
            "global_access_policy": valid_json["global_access_policy"],  # Include the actual policy
            "group_access_policy": valid_json.get("group_access_policy"),
            "user_specific_access_policy": valid_json.get("user_specific_access_policy"),
        })
        
        mock_collection.update_one = AsyncMock(return_value=mock.Mock(matched_count=1))

        # Act
        response = await RulesetManagerService.update_ruleset(tenant_id, ruleset_name, update_request)

        # Assert
        assert response["message"] == "Ruleset updated successfully"


    @mock.patch('api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_delete_ruleset_success(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "ecommerce_ruleset"

        mock_get_tenant.return_value = Tenant(tenant_id=tenant_id, tenant_name="Test Tenant")
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.delete_one = AsyncMock(return_value=mock.Mock(deleted_count=1))

        # Act
        response = await RulesetManagerService.delete_ruleset(tenant_id, ruleset_name)

        # Assert
        assert response == {"message": "Ruleset deleted successfully"}

    @mock.patch('api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_delete_ruleset_not_found(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "non_existent_ruleset"
        mock_get_tenant.return_value = Tenant(tenant_id=tenant_id, tenant_name="Test Tenant")
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.delete_one = AsyncMock(return_value=mock.Mock(deleted_count=0))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await RulesetManagerService.delete_ruleset(tenant_id, ruleset_name)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Ruleset not found"
