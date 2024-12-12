import pytest
import json
from unittest import mock
from fastapi import HTTPException
from model.requests.tenant_manager.add_setting_to_tenant_request import AddSettingToTenantRequest
from model.tenant import Tenant
from model.setting import Setting
from api.core.services.tenant_manager.tenant_settings_service import TenantSettingsService
from tests.testing_utilities.test_utils import RESOURCES_PATH

@pytest.mark.asyncio
class TestTenantSettingsService:

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_add_settings_to_tenant_success(self, mock_get_tenant, mock_db):
        # Assert
        tenant_id = "tenant1"
        tenant_dict = {"tenant_id": tenant_id, "tenant_name": "Test Tenant", "settings": {}}
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        add_settings_request = AddSettingToTenantRequest(
            __root__={key: Setting(**value) for key, value in valid_settings.items()}
        )

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(modified_count=1)

        # Act
        result = await TenantSettingsService.add_settings_to_tenant(tenant_id, add_settings_request)
        
        mock_collection.update_one.assert_called_once_with(
            {"tenant_id": tenant_id},
            {"$set": {"settings": {key: value.dict() for key, value in add_settings_request.__root__.items()}}},
            upsert=False
        )
        
        # Assert
        assert result == {
            "message": "Settings inserted successfully into tenant",
            "new_settings": {key: value.dict() for key, value in add_settings_request.__root__.items()}
        }

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_add_settings_to_tenant_conflict(self, mock_get_tenant, mock_db):
        # Act
        tenant_id = "tenant1"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {
                "BASE_MODEL_LLM_URL": Setting(
                    setting_basic_name="Base Model LLM URL",
                    setting_value="value",
                    setting_category="LLM_GENERATION",
                    is_custom_setting=False
                ).dict()
            }
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        add_settings_request = AddSettingToTenantRequest(
            __root__={key: Setting(**value) for key, value in valid_settings.items()}
        )
        
        # Act
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.add_settings_to_tenant(tenant_id, add_settings_request)
        
        # Assert
        assert excinfo.value.status_code == 400
        assert "Setting keys already exist for this tenant" in excinfo.value.detail

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_update_settings_to_tenant_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {
                "BASE_MODEL_LLM_URL": {
                    "setting_basic_name": "Base Model LLM URL",
                    "setting_value": "Old Value",
                    "setting_category": "LLM_GENERATION",
                    "is_custom_setting": False,
                }
            },
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        update_settings_request = AddSettingToTenantRequest(
            __root__={key: Setting(**value) for key, value in valid_settings.items()}
        )

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(modified_count=1)

        # Act
        result = await TenantSettingsService.update_settings_to_tenant(tenant_id, update_settings_request)
        
        mock_collection.update_one.assert_called_once_with(
            {"tenant_id": tenant_id},
            {"$set": {"settings": {key: value.dict() for key, value in update_settings_request.__root__.items()}}},
            upsert=False
        )
        
        # Assert
        assert result == {
            "message": "Settings updated successfully for tenant",
            "updated_settings": {key: value.dict() for key, value in update_settings_request.__root__.items()}
        }

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_update_settings_to_tenant_no_change(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {key: value for key, value in valid_settings.items()},
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        update_settings_request = AddSettingToTenantRequest(
            __root__={key: Setting(**value) for key, value in valid_settings.items()}
        )

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        
        # Act
        result = await TenantSettingsService.update_settings_to_tenant(tenant_id, update_settings_request)

        mock_collection.update_one.assert_not_called()
        
        # Assert
        assert result == {"message": "No changes to settings were made."}

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_update_settings_to_tenant_failure(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {
                "BASE_MODEL_LLM_URL": {
                    "setting_basic_name": "Base Model LLM URL",
                    "setting_value": "Old Value",
                    "setting_category": "LLM_GENERATION",
                    "is_custom_setting": False,
                }
            },
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        with open(f'{RESOURCES_PATH}/settings/valid/valid_default_settings.json', 'r') as file:
            valid_settings = json.load(file)

        update_settings_request = AddSettingToTenantRequest(
            __root__={key: Setting(**value) for key, value in valid_settings.items()}
        )

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(modified_count=0)
        
        # Act
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.update_settings_to_tenant(tenant_id, update_settings_request)
        
        # Assert
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Failed to update settings for tenant"


    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_delete_setting_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        setting_key = "CUSTOM_SETTING"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",  # Add this field
            "settings": {
                setting_key: Setting(
                    setting_basic_name="Custom Setting",
                    setting_value="value",
                    setting_category="CATEGORY",
                    is_custom_setting=True
                ).dict()
            }
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(modified_count=1)

        # Act
        result = await TenantSettingsService.delete_setting(tenant_id, setting_key)

        # Assert
        mock_collection.update_one.assert_called_once_with(
            {"tenant_id": tenant_id},
            {"$set": {"settings": {}}},
            upsert=False
        )
        assert result["message"] == f"Setting '{setting_key}' successfully deleted for tenant {tenant_id}"
        assert result["updated_settings"] == {}

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_delete_setting_not_found(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        setting_key = "NON_EXISTENT_SETTING"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant", 
            "settings": {}
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        # Act 
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.delete_setting(tenant_id, setting_key)
            
        # Assert
        assert excinfo.value.status_code == 404
        assert f"Tenant '{tenant_id}' or setting key '{setting_key}' not found" in excinfo.value.detail

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_delete_setting_default_cannot_be_deleted(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        setting_key = "DEFAULT_SETTING"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",  
            "settings": {
                setting_key: Setting(
                    setting_basic_name="Default Setting",
                    setting_value="value",
                    setting_category="CATEGORY",
                    is_custom_setting=False
                ).dict()
            }
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        # Act
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.delete_setting(tenant_id, setting_key)
            
        # Assert
        assert excinfo.value.status_code == 400
        assert f"Default setting '{setting_key}' cannot be deleted" in excinfo.value.detail

    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_delete_setting_update_failed(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        setting_key = "CUSTOM_SETTING"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",  
            "settings": {
                setting_key: Setting(
                    setting_basic_name="Custom Setting",
                    setting_value="value",
                    setting_category="CATEGORY",
                    is_custom_setting=True
                ).dict()
            }
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.side_effect = lambda key: mock_collection if key == "tenants" else None
        mock_collection.update_one.return_value = mock.Mock(modified_count=0)

        # Act 
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.delete_setting(tenant_id, setting_key)
            
        # Assert
        assert excinfo.value.status_code == 400
        assert f"Failed to delete setting '{setting_key}' for tenant {tenant_id}" in excinfo.value.detail
        
        
    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_get_settings_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {
                "BASE_MODEL_LLM_URL": {
                    "setting_basic_name": "Base Model LLM URL",
                    "setting_value": "{BASE_URL_FOR_LLM_API_URL}",
                    "setting_category": "LLM_GENERATION",
                    "is_custom_setting": False,
                }
            },
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        # Act
        result = await TenantSettingsService.get_settings(tenant_id)

        # Assert
        assert result == {"settings": tenant.settings}
        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)


    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_get_settings_not_found(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "nonexistent_tenant"
        mock_get_tenant.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.get_settings(tenant_id)
            
        assert excinfo.value.status_code == 404
        assert f"Tenant with id {tenant_id} not found" in excinfo.value.detail
        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)


    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_get_setting_detail_success(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        setting_key = "BASE_MODEL_LLM_URL"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {
                setting_key: {
                    "setting_basic_name": "Base Model LLM URL",
                    "setting_value": "{BASE_URL_FOR_LLM_API_URL}",
                    "setting_category": "LLM_GENERATION",
                    "is_custom_setting": False,
                }
            },
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        # Act
        result = await TenantSettingsService.get_setting_detail(tenant_id, setting_key)

        # Assert
        assert result == {
            "setting_key": setting_key,
            "setting_detail": {
                "setting_basic_name": "Base Model LLM URL",
                "setting_value": "{BASE_URL_FOR_LLM_API_URL}",
                "setting_category": "LLM_GENERATION",
                "is_custom_setting": False,
            },
        }
        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)


    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_get_setting_detail_not_found(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "tenant1"
        setting_key = "NON_EXISTENT_SETTING"
        tenant_dict = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",
            "settings": {
                "BASE_MODEL_LLM_URL": {
                    "setting_basic_name": "Base Model LLM URL",
                    "setting_value": "{BASE_URL_FOR_LLM_API_URL}",
                    "setting_category": "LLM_GENERATION",
                    "is_custom_setting": False,
                }
            },
        }
        tenant = Tenant(**tenant_dict)
        mock_get_tenant.return_value = tenant

        # Act
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.get_setting_detail(tenant_id, setting_key)
            
        # Assert
        assert excinfo.value.status_code == 404
        assert f"Tenant '{tenant_id}' or setting key '{setting_key}' not found" in excinfo.value.detail
        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)


    @mock.patch("utils.database.mongodb.db")
    @mock.patch("api.core.services.tenant_manager.tenant_manager_service.TenantManagerService.get_tenant")
    async def test_get_setting_detail_tenant_not_found(self, mock_get_tenant, mock_db):
        # Arrange
        tenant_id = "nonexistent_tenant"
        setting_key = "BASE_MODEL_LLM_URL"
        mock_get_tenant.return_value = None

        # Act
        with pytest.raises(HTTPException) as excinfo:
            await TenantSettingsService.get_setting_detail(tenant_id, setting_key)
            
        # Assert
        assert excinfo.value.status_code == 404
        assert f"Tenant '{tenant_id}' or setting key '{setting_key}' not found" in excinfo.value.detail
        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)
