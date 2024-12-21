import pytest
from unittest import mock
from fastapi import HTTPException

from model.tenant import Tenant
from utils.database import mongodb
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel
from model.responses.tenant_manager.add_tenant_response import AddTenantResponse 

@pytest.mark.asyncio
class TestTenantManagerService:

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("utils.tenant_manager.setting_utils.SettingUtils.initialize_default_tenant_settings")
    async def test_add_tenant(self, mock_initialize_settings, mock_db):
        # Arrange
        tenant_data = Tenant(tenant_id="tenant123", tenant_name="Tenant 123")
        tenant_dict = tenant_data.dict()
        tenant_dict["settings"] = {}
        
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.side_effect = [None, tenant_dict]
        mock_initialize_settings.return_value = {"settings": {}}

        # Act
        result = await TenantManagerService.add_tenant(tenant_data)

        # Assert
        mock_collection.insert_one.assert_called_once_with(tenant_data.dict())
        mock_initialize_settings.assert_called_once_with(tenant_id="tenant123")
        mock_collection.find_one.assert_called_with({"tenant_id": "tenant123"})
        assert result["message"] == "Tenant created successfully"
        assert result["tenant"] == AddTenantResponse(**tenant_dict)

    @mock.patch("utils.database.mongodb.db")
    async def test_add_tenant_already_exists(self, mock_db):
        # Arrange
        tenant_data = Tenant(tenant_id="tenant123", tenant_name="Tenant 123")
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {"tenant_id": "tenant123"}

        # Act
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.add_tenant(tenant_data)
            
        # Assert
        assert exc.value.status_code == 400
        assert exc.value.detail == "A tenant with this tenant_id already exists"

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("utils.tenant_manager.setting_utils.SettingUtils.initialize_default_tenant_settings")
    async def test_add_tenant_initialization_failure(self, mock_initialize_settings, mock_db):
        # Arrange
        tenant_data = Tenant(tenant_id="tenant123", tenant_name="Tenant 123")
        _ = tenant_data.dict()
        
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.side_effect = [None]
        mock_initialize_settings.side_effect = Exception("Initialization failed")

        # Act
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.add_tenant(tenant_data)

        mock_collection.insert_one.assert_called_once_with(tenant_data.dict())
        mock_initialize_settings.assert_called_once_with(tenant_id="tenant123")
        mock_collection.delete_one.assert_called_once_with({"tenant_id": "tenant123"})
        
        # Assert
        assert exc.value.status_code == 500
        assert "Failed to initialize tenant" in exc.value.detail
        
        
    @mock.patch("utils.database.mongodb.db")
    async def test_get_tenant(self, mock_db):
        # Arrange
        tenant_data = {"tenant_id": "tenant123", "tenant_name": "Tenant 123"}
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = tenant_data

        # Act
        tenant = await TenantManagerService.get_tenant("tenant123")

        # Assert
        assert tenant.tenant_id == "tenant123"
        assert tenant.tenant_name == "Tenant 123"

    @mock.patch("utils.database.mongodb.db")
    async def test_get_tenant_not_found(self, mock_db):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = None  

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.get_tenant("non_existent_tenant")

        assert exc.value.status_code == 404
        assert exc.value.detail == "Tenant not found"

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_delete_tenant(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant123"

        # Mock tenant exists
        mock_get_tenant.return_value = {"tenant_id": tenant_id, "settings": {}}

        # Mock database collections
        mock_tenants_collection = mock.AsyncMock()
        mock_schemas_collection = mock.AsyncMock()
        mock_rulesets_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "tenants": mock_tenants_collection,
            "schemas": mock_schemas_collection,
            "rulesets": mock_rulesets_collection
        }[name]

        # Mock database delete responses
        mock_schemas_collection.delete_many.return_value = mock.AsyncMock(deleted_count=3)
        mock_rulesets_collection.delete_many.return_value = mock.AsyncMock(deleted_count=2)
        mock_tenants_collection.delete_one.return_value = mock.AsyncMock(deleted_count=1)

        # Act
        result = await TenantManagerService.delete_tenant(tenant_id)

        # Assert
        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)
        mock_schemas_collection.delete_many.assert_called_once_with({"tenant_id": tenant_id})
        mock_rulesets_collection.delete_many.assert_called_once_with({"tenant_id": tenant_id})
        mock_tenants_collection.delete_one.assert_called_once_with({"tenant_id": tenant_id})
        assert result == {
            "message": "Tenant and associated orphan data deleted successfully",
            "schemas_deleted": 3,
            "rulesets_deleted": 2
        }

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_delete_tenant_not_found(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "non_existent_tenant"

        # Mock tenant does not exist
        mock_get_tenant.side_effect = HTTPException(status_code=404, detail="Tenant not found")

        mock_tenants_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_tenants_collection
        mock_tenants_collection.delete_one.return_value = mock.AsyncMock(deleted_count=0)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.delete_tenant(tenant_id)

        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)
        mock_tenants_collection.delete_one.assert_not_called()  # Ensure no deletion attempted
        assert exc.value.status_code == 404
        assert exc.value.detail == "Tenant not found"


    @mock.patch("utils.database.mongodb.db")
    async def test_update_tenant(self, mock_db):
        # Arrange
        tenant_data = UpdateTenantRequestModel(tenant_name="Updated Tenant") 
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.update_one.return_value = mock.AsyncMock(matched_count=1)  

        # Act
        result = await TenantManagerService.update_tenant("tenant123", tenant_data)

        # Assert
        mock_collection.update_one.assert_called_once_with(
            {"tenant_id": "tenant123"}, 
            {"$set": {"tenant_name": "Updated Tenant"}}
        )
        assert result == {"message": "Tenant updated successfully"}

    @mock.patch("utils.database.mongodb.db")
    async def test_update_tenant_not_found(self, mock_db):
        # Arrange
        tenant_data = UpdateTenantRequestModel(tenant_name="Updated Tenant")
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.update_one.return_value = mock.AsyncMock(matched_count=0) 

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.update_tenant("non_existent_tenant", tenant_data)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Tenant not found"