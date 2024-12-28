import pytest
from unittest import mock
from fastapi import HTTPException
from model.tenant.tenant import Tenant
from utils.database import mongodb
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from model.requests.tenant_manager.update_tenant_request import UpdateTenantRequestModel
from model.responses.tenant_manager.add_tenant_response import AddTenantResponse



@pytest.mark.asyncio
class TestTenantManagerService:


    def _initialize_mock_data(self):
        tenant_id = "TENANT123"
        tenant_name = "TENANT 123"

        tenant_data = Tenant(tenant_id=tenant_id, tenant_name=tenant_name)
        tenant_dict = tenant_data.dict()
        tenant_dict["settings"] = {}

        update_tenant_request = UpdateTenantRequestModel(tenant_name="UPDATED TENANT")

        valid_settings = {
            "settings": {
                "LLM_GENERATION": {
                    "BASE_MODEL_LLM_URL": {
                        "setting_basic_name": "Base Model LLM URL",
                        "setting_value": "http://example.com",
                        "is_custom_setting": False
                    }
                }
            }
        }

        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "tenant_data": tenant_data,
            "tenant_dict": tenant_dict,
            "update_tenant_request": update_tenant_request,
            "valid_settings": valid_settings,
        }

    @mock.patch("utils.tenant_manager.tenant_utils.TenantUtils.initialize_tenant_tokens")
    @mock.patch("utils.tenant_manager.tenant_utils.TenantUtils.initialize_default_admin_user")
    @mock.patch("utils.tenant_manager.setting_utils.SettingUtils.initialize_default_tenant_settings")
    @mock.patch("utils.database.mongodb.db")
    async def test_add_tenant(
        self,
        mock_db,
        mock_initialize_settings,
        mock_initialize_admin_user,
        mock_initialize_tokens
    ):
        # Arrange
        mock_data = self._initialize_mock_data()
        tenant_data = mock_data["tenant_data"]
        tenant_dict = mock_data["tenant_dict"]

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.side_effect = [None, tenant_dict]

        mock_initialize_settings.return_value = {"settings": {}}
        mock_initialize_admin_user.return_value = {"message": "Default admins initialized successfully"}
        mock_initialize_tokens.return_value = {"message": "Tenant tokens initialized successfully"}

        # Act
        result = await TenantManagerService.add_tenant(tenant_data)

        # Assert
        mock_collection.insert_one.assert_called_once_with(tenant_data.dict())
        mock_initialize_settings.assert_called_once_with(tenant_id=mock_data["tenant_id"])
        mock_initialize_admin_user.assert_called_once_with(tenant_id=mock_data["tenant_id"])
        mock_initialize_tokens.assert_called_once_with(tenant_id=mock_data["tenant_id"])
        mock_collection.find_one.assert_called_with({"tenant_id": mock_data["tenant_id"]})
        assert result["message"] == "Tenant created successfully"

    @mock.patch("utils.database.mongodb.db")
    async def test_add_tenant_already_exists(self, mock_db):
        # Arrange
        mock_data = self._initialize_mock_data()
        tenant_data = mock_data["tenant_data"]

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = {"tenant_id": mock_data["tenant_id"]}

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.add_tenant(tenant_data)

        assert exc.value.status_code == 400
        assert exc.value.detail == "A tenant with this tenant_id already exists"

    @mock.patch("utils.database.mongodb.db")
    async def test_get_tenant(self, mock_db):
        # Arrange
        mock_data = self._initialize_mock_data()

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = mock_data["tenant_dict"]

        # Act
        tenant = await TenantManagerService.get_tenant(mock_data["tenant_id"])

        # Assert
        assert tenant.tenant_id == mock_data["tenant_id"]
        assert tenant.tenant_name == mock_data["tenant_name"]

    @mock.patch("utils.database.mongodb.db")
    async def test_get_tenant_not_found(self, mock_db):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.get_tenant("NON_EXISTENT_TENANT")

        assert exc.value.status_code == 404
        assert exc.value.detail == "Tenant not found"

    @mock.patch("utils.database.mongodb.db")
    async def test_update_tenant(self, mock_db):
        # Arrange
        mock_data = self._initialize_mock_data()
        update_request = mock_data["update_tenant_request"]

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.update_one.return_value = mock.AsyncMock(matched_count=1)

        # Act
        result = await TenantManagerService.update_tenant(mock_data["tenant_id"], update_request)

        # Assert
        mock_collection.update_one.assert_called_once_with(
            {"tenant_id": mock_data["tenant_id"]},
            {"$set": {"tenant_name": "UPDATED TENANT"}}
        )
        assert result == {"message": "Tenant updated successfully"}

    @mock.patch("utils.database.mongodb.db")
    async def test_update_tenant_not_found(self, mock_db):
        # Arrange
        mock_data = self._initialize_mock_data()
        update_request = mock_data["update_tenant_request"]

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.update_one.return_value = mock.AsyncMock(matched_count=0)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await TenantManagerService.update_tenant("NON_EXISTENT_TENANT", update_request)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Tenant not found"

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_delete_tenant(self, mock_get_tenant, mock_db):
        # Arrange
        mock_data = self._initialize_mock_data()
        tenant_id = mock_data["tenant_id"]

        mock_get_tenant.return_value = {"tenant_id": tenant_id, "settings": {}}

        mock_tenants_collection = mock.AsyncMock()
        mock_schemas_collection = mock.AsyncMock()
        mock_rulesets_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "tenants": mock_tenants_collection,
            "schemas": mock_schemas_collection,
            "rulesets": mock_rulesets_collection
        }[name]

        mock_schemas_collection.delete_many.return_value = mock.AsyncMock(deleted_count=3)
        mock_rulesets_collection.delete_many.return_value = mock.AsyncMock(deleted_count=2)
        mock_tenants_collection.delete_one.return_value = mock.AsyncMock(deleted_count=1)

        # Act
        result = await TenantManagerService.delete_tenant(tenant_id)

        # Assert
        assert result == {
            "message": "Tenant and associated orphan data deleted successfully",
            "schemas_deleted": 3,
            "rulesets_deleted": 2
        }