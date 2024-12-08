import pytest
import json
from unittest import mock
from unittest.mock import AsyncMock
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from api.core.services.ruleset_manager.ruleset_manager_service import RulesetManagerService
from model.requests.ruleset_manager.add_ruleset_request import AddRulesetRequest
from model.responses.ruleset_manager.ruleset_response import RulesetResponse
from model.ruleset import Ruleset
from utils.database import mongodb
from model.tenant import Tenant
from pydantic import ValidationError
from tests.utils.test_utils import RESOURCES_PATH

@pytest.mark.asyncio
class TestSchemaManagerService:

    @mock.patch('utils.database.mongodb.db')
    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    async def test_add_ruleset_invalid_json_fail(self, mock_get_tenant, mock_db):
        # Arrange
        with open(f'{RESOURCES_PATH}/rulesets/invalid/ecommerce_ruleset_invalid.json', 'r') as file:
            invalid_json = json.load(file)

        mock_collection = mock.Mock()
        mock_db["rulesets"] = mock_collection 

        mock_get_tenant.return_value = Tenant(
            tenant_id="tenant_123", 
            tenant_name="Test Tenant"
        )

        # Act
        with pytest.raises(ValidationError) as exc_info:
            _ = AddRulesetRequest(**invalid_json)
              
        #Assert    
        assert 'table_access_policy' in str(exc_info.value)  
        assert 'columns' in str(exc_info.value)  
        assert 'condition' in str(exc_info.value) 
        
    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_add_ruleset_with_user_specific_policy_success(self, mock_db, mock_get_tenant):
        # Arrange
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_tenant.return_value = Tenant(
            tenant_id="tenant_123",
            tenant_name="Test Tenant"
        )
        valid_request = AddRulesetRequest(**valid_json)

        mock_collection.insert_one = AsyncMock(return_value=mock.Mock(inserted_id="mock_id"))
        response = await RulesetManagerService.add_ruleset("tenant_123", valid_request)
        expected_data = valid_request.dict()
        expected_data["tenant_id"] = "tenant_123"

        # Act
        mock_collection.insert_one.assert_called_once_with(expected_data)

        # Assert 
        assert response == {"message": "Ruleset added successfully", "ruleset_id": "mock_id"}

    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_add_ruleset_without_user_specific_policy_success(self, mock_db, mock_get_tenant):
        # Arrange
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_without_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_tenant.return_value = Tenant(
            tenant_id="tenant_123",
            tenant_name="Test Tenant"
        )
        valid_request = AddRulesetRequest(**valid_json)

        mock_collection.insert_one = AsyncMock(return_value=mock.Mock(inserted_id="mock_id"))
        response = await RulesetManagerService.add_ruleset("tenant_123", valid_request)

        # Adjust the expected data to include tenant_id
        expected_data = valid_request.dict()
        expected_data["tenant_id"] = "tenant_123"

        # Act
        mock_collection.insert_one.assert_called_once_with(expected_data)

        # Assert
        assert response == {"message": "Ruleset added successfully", "ruleset_id": "mock_id"}
        
    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_get_ruleset_success(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "ecommerce_ruleset2"
        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        valid_json["description"] = valid_json.get("description", "Default description")
        valid_json["global_access_policy"] = valid_json.get("global_access_policy", {})
        valid_json["table_access_policy"] = valid_json.get("table_access_policy", {})
        valid_json["default_action"] = valid_json.get("default_action", "ALLOW")  
        valid_json["tenant_id"] = tenant_id

        mock_collection.find_one = AsyncMock(return_value=valid_json)

        # Act
        response = await RulesetManagerService.get_ruleset(tenant_id, ruleset_name)

        # Assert
        mock_collection.find_one.assert_called_once_with({"tenant_id": tenant_id, "ruleset_name": ruleset_name})
        assert response.tenant_id == tenant_id
        assert response.ruleset_name == ruleset_name
        assert response.description == valid_json["description"]
        assert response.global_access_policy == valid_json["global_access_policy"]
        assert response.table_access_policy == valid_json["table_access_policy"]
        

    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_get_ruleset_not_found(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "non_existent_ruleset"
        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one = AsyncMock(return_value=None)

        # Act 
        with pytest.raises(HTTPException) as exc_info:
            await RulesetManagerService.get_ruleset(tenant_id, ruleset_name)
        
        mock_collection.find_one.assert_called_once_with({"tenant_id": tenant_id, "ruleset_name": ruleset_name})
        
        # Assert
        assert exc_info.value.status_code == 404
        assert "No Ruleset found" in exc_info.value.detail


    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_update_ruleset_not_found(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "non_existent_ruleset"
        
        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        update_request = AddRulesetRequest(**valid_json)

        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )

        # Act
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await RulesetManagerService.update_ruleset(tenant_id, ruleset_name, update_request)

        mock_collection.find_one.assert_called_once_with({"tenant_id": tenant_id, "ruleset_name": ruleset_name})
        # Assert
        assert exc_info.value.status_code == 404
        assert "Ruleset with name" in exc_info.value.detail


    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_update_ruleset_no_changes(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "ecommerce_ruleset"

        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        update_request = AddRulesetRequest(**valid_json)

        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection

        # Act
        mock_collection.find_one = AsyncMock(return_value={
            "tenant_id": tenant_id,
            "ruleset_name": ruleset_name,
            "description": "Existing description",
            "default_action": "ALLOW",
            "global_access_policy": {"tables": {"users": {"columns": {"allow": "*", "deny": []}, "condition": "TRUE"}}},
            "table_access_policy": {"tables": {"users": {"columns": {"allow": "*", "deny": []}, "condition": "TRUE"}}},
            "user_specific_access_policy": []
        })
        mock_collection.update_one = AsyncMock(return_value=AsyncMock(matched_count=1))

        response = await RulesetManagerService.update_ruleset(tenant_id, ruleset_name, update_request)

        mock_collection.update_one.assert_called_once_with(
            {"tenant_id": tenant_id, "ruleset_name": ruleset_name},
            {"$set": update_request.dict(exclude_unset=True)}
        )
        
        # Assert
        assert response["message"] == "Ruleset updated successfully"
        assert response["updated_ruleset"].ruleset_name == ruleset_name
        assert response["updated_ruleset"].tenant_id == tenant_id

    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_update_ruleset_success(self, mock_db, mock_get_tenant):
        # Assert
        tenant_id = "tenant_123"
        ruleset_name = "ecommerce_ruleset"

        with open(f'{RESOURCES_PATH}/rulesets/valid/ecommerce_ruleset_with_user_specific_policy.json', 'r') as file:
            valid_json = json.load(file)

        update_request = AddRulesetRequest(**valid_json)

        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.side_effect = [
            {
                "tenant_id": tenant_id,
                "ruleset_name": ruleset_name,
                "description": "Existing description",
                "default_action": "ALLOW",
                "global_access_policy": {"tables": {"users": {"columns": {"allow": "*", "deny": []}, "condition": "TRUE"}}},
                "table_access_policy": {"tables": {"users": {"columns": {"allow": "*", "deny": []}, "condition": "TRUE"}}},
                "user_specific_access_policy": []
            },
            {  # Mock updated ruleset
                "tenant_id": tenant_id,
                "ruleset_name": "ecommerce_ruleset2",
                "description": "Ruleset for managing access to the e-commerce schema with JWT-based user context",
                "default_action": "DENY",
                "global_access_policy": {"tables": {"users": {"columns": {"allow": "*", "deny": ["password"]}, "condition": "TRUE"}}},
                "table_access_policy": {
                    "tables": {
                        "users": {"columns": {"allow": ["user_id", "name", "email"], "deny": ["password"]}, "condition": "users.user_id = ${jwt.user_id}"},
                        "orders": {"columns": {"allow": ["order_id", "amount", "user_id"], "deny": ["status"]}, "condition": "orders.user_id = ${jwt.user_id} OR ${jwt.role} = 'admin'"}
                    }
                },
                "user_specific_access_policy": [
                    {
                        "user_identifier": "string@example.com",
                        "tables": {"users": {"columns": {"allow": ["id", "email"], "deny": []}, "condition": "TRUE"}}
                    }
                ]
            }
        ]

        # Act
        mock_collection.update_one = AsyncMock(return_value=AsyncMock(matched_count=1))

        response = await RulesetManagerService.update_ruleset(tenant_id, ruleset_name, update_request)

        mock_collection.update_one.assert_called_once_with(
            {"tenant_id": tenant_id, "ruleset_name": ruleset_name},
            {"$set": {
                "ruleset_name": "ecommerce_ruleset2",
                "description": "Ruleset for managing access to the e-commerce schema with JWT-based user context",
                "default_action": "DENY",
                "global_access_policy": {"tables": {"users": {"columns": {"allow": "*", "deny": ["password"]}, "condition": "TRUE"}}},
                "table_access_policy": {
                    "tables": {
                        "users": {"columns": {"allow": ["user_id", "name", "email"], "deny": ["password"]}, "condition": "users.user_id = ${jwt.user_id}"},
                        "orders": {"columns": {"allow": ["order_id", "amount", "user_id"], "deny": ["status"]}, "condition": "orders.user_id = ${jwt.user_id} OR ${jwt.role} = 'admin'"}
                    }
                },
                "user_specific_access_policy": [
                    {
                        "user_identifier": "string@example.com",
                        "tables": {"users": {"columns": {"allow": ["id", "email"], "deny": []}, "condition": "TRUE"}}
                    }
                ]
            }}
        )
        
        # Assert
        assert response["message"] == "Ruleset updated successfully"
        assert response["updated_ruleset"].ruleset_name == "ecommerce_ruleset2"


    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_update_ruleset_invalid(self, mock_db, mock_get_tenant):
        # Assert
        tenant_id = "tenant_123"
        ruleset_name = "invalid_ruleset"
      
        invalid_json = {
            "ruleset_name": "invalid_ruleset",
            "description": "Invalid ruleset",
            "default_action": "DENY",
            "global_access_policy": {"tables": {"users": {"columns": {"allow": "*", "deny": []}, "condition": "TRUE"}}},
            "table_access_policy": {
                "tables": {
                    "users": {}  
                }
            }
        }

        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )

        # Act
        with pytest.raises(ValidationError) as exc_info:
            AddRulesetRequest(**invalid_json)

        # Assert
        assert "Table 'users' in table_access_policy must contain 'columns' and 'condition'" in str(exc_info.value)


    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_delete_ruleset_success(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "ecommerce_ruleset"
        
        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection

        # Simulate a successful delete
        mock_collection.delete_one = AsyncMock(return_value=AsyncMock(deleted_count=1))

        # Act
        response = await RulesetManagerService.delete_ruleset(tenant_id, ruleset_name)

        # Assert
        mock_collection.delete_one.assert_called_once_with({"tenant_id": tenant_id, "ruleset_name": ruleset_name})
        assert response == {"message": "Ruleset deleted successfully"}
        

    @mock.patch('api.core.services.ruleset_manager.ruleset_manager_service.TenantManagerService.get_tenant')
    @mock.patch('utils.database.mongodb.db')
    async def test_delete_ruleset_not_found(self, mock_db, mock_get_tenant):
        # Arrange
        tenant_id = "tenant_123"
        ruleset_name = "nonexistent_ruleset"

        mock_get_tenant.return_value = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant"
        )

        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection

        # Simulate no document deleted
        mock_collection.delete_one = AsyncMock(return_value=AsyncMock(deleted_count=0))

        # Act 
        with pytest.raises(HTTPException) as exc_info:
            await RulesetManagerService.delete_ruleset(tenant_id, ruleset_name)

        mock_collection.delete_one.assert_called_once_with({"tenant_id": tenant_id, "ruleset_name": ruleset_name})
        
        # Assert
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Ruleset not found"