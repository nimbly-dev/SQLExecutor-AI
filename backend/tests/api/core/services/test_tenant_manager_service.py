import pytest
from unittest import mock
from fastapi import HTTPException

from model.tenant import Tenant
from utils.database import mongodb
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel 


@pytest.mark.asyncio
class TestTenantManagerService:

    @mock.patch("utils.database.mongodb.db")
    async def test_add_tenant(self, mock_db):
        # Arrange
        tenant_data = Tenant(tenant_id="tenant123", tenant_name="Tenant 123")
        mock_collection = mock.AsyncMock()  
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = None  

        # Act
        result = await TenantManagerService.add_tenant(tenant_data)

        # Assert
        mock_collection.insert_one.assert_called_once_with(tenant_data.dict())
        assert result == {"message": "Tenant created successfully"}

    @mock.patch("utils.database.mongodb.db")
    async def test_add_tenant_already_exists(self, mock_db):
        # Arrange
        tenant_data = Tenant(tenant_id="tenant123", tenant_name="Tenant 123")
        mock_collection = mock.AsyncMock()  
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {"tenant_id": "tenant123"}  

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.add_tenant(tenant_data)

        assert exc.value.status_code == 400
        assert exc.value.detail == "A tenant with this tenant_id already exists"
        
        
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
    async def test_delete_tenant(self, mock_db):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.delete_one.return_value = mock.AsyncMock(deleted_count=1)  

        # Act
        result = await TenantManagerService.delete_tenant("tenant123")

        # Assert
        mock_collection.delete_one.assert_called_once_with({"tenant_id": "tenant123"})
        assert result == {"message": "Tenant deleted successfully"}

    @mock.patch("utils.database.mongodb.db")
    async def test_delete_tenant_not_found(self, mock_db):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.delete_one.return_value = mock.AsyncMock(deleted_count=0)  

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.delete_tenant("non_existent_tenant")

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