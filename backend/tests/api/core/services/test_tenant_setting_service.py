import pytest
import json
from unittest import mock
from fastapi import HTTPException
from model.requests.tenant_manager.add_setting_to_tenant_request import AddSettingToTenantRequest
from model.requests.tenant_manager.update_setting_to_tenant_request import UpdateSettingRequest
from model.tenant import Tenant
from model.setting import Setting
from api.core.services.tenant_manager.tenant_settings_service import TenantSettingsService
from tests.testing_utilities.test_utils import RESOURCES_PATH

@pytest.mark.asyncio
class TestTenantSettingsService:

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_add_settings_to_tenant_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        tenant_dict = {"tenant_id": tenant_id, "tenant_name": "Test Tenant", "settings": {}}
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        add_settings_request = AddSettingToTenantRequest(
            __root__={key: {k: Setting(**v) for k, v in value.items()} for key, value in valid_settings["settings"].items()}
        )

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(modified_count=1)

        # Act
        result = await TenantSettingsService.add_settings_to_tenant(tenant_id, add_settings_request)
        
        # Assert
        assert result["new_settings"] == tenant.settings

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_update_cat_settings_to_tenant_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        category_key = "LLM_GENERATION"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {category_key: {}}
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        update_settings_request = UpdateSettingRequest(
            __root__={key: Setting(**value) for key, value in valid_settings["settings"][category_key].items()}
        )

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(modified_count=1)

        # Act
        result = await TenantSettingsService.update_cat_settings_to_tenant(tenant_id, category_key, update_settings_request)
        
        # Assert
        assert result is not None

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_get_setting_detail_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        category_key = "LLM_GENERATION"
        setting_key = "BASE_MODEL_LLM_URL"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {
                category_key: {
                    setting_key: Setting(
                        setting_description="Test Desc",
                        setting_basic_name="Test Name",
                        setting_default_value="default",
                        setting_value="value",
                        is_custom_setting=False
                    )
                }
            }
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        # Act
        result = await TenantSettingsService.get_setting_detail(tenant_id, category_key, setting_key)
        
        # Assert
        assert result["setting_detail"] == tenant.settings[category_key][setting_key].dict()

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_update_cat_settings_to_tenant_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        category_key = "LLM_GENERATION"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {category_key: {}}
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        update_settings_request = UpdateSettingRequest(
            __root__={key: Setting(**value) for key, value in valid_settings["settings"][category_key].items()}
        )

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(matched_count=1, modified_count=1)

        # Act
        result = await TenantSettingsService.update_cat_settings_to_tenant(tenant_id, category_key, update_settings_request)

        # Assert
        assert result == {
            "message": f"Category '{category_key}' settings updated successfully.",
            "updated_settings": {key: value.dict() for key, value in update_settings_request.__root__.items()}
        }
