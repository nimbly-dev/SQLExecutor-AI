# tests/api/core/services/test_api_context_integration_service.py

import pytest
from unittest import mock
from fastapi import HTTPException
from api.core.services.external_system.api_context.api_context_integration_service import APIContextIntegrationService
from model.tenant.tenant import Tenant
from model.requests.external_system_integration.fetch_external_context_request import CreateExternalSessionRequest
from model.authentication.external_user_decoded_jwt_token import DecodedJwtToken
from model.tenant.setting import Setting
from api.core.constants.tenant.settings_categories import (
    API_CONTEXT_INTEGRATION,
    API_KEYS,
    FRONTEND_SANDBOX_CHAT_INTERFACE,
    EXTERNAL_JWT_AUTH_CATEGORY_KEY
)
from utils.tenant_manager.setting_utils import SettingUtils
import aiohttp
import jwt
import hmac
import hashlib
import time
from datetime import datetime, timezone


def get_mock_tenant():
    return Tenant(
        tenant_id="TENANT_TST1",
        tenant_name="Test Tenant",
        admins=[],
        settings={
            API_CONTEXT_INTEGRATION: {
                "EXTERNAL_API_CONTEXT_GET_USER_ENDPOINT": Setting(
                    setting_basic_name="External API Context Get User Endpoint",
                    setting_value="https://external.api/get-user",
                    setting_description="Endpoint to fetch user data",
                    is_custom_setting=False
                ),
                "EXTERNAL_API_CONTEXT_GET_USERS_ENDPOINT": Setting(
                    setting_basic_name="External Context Get Users API Endpoint",
                    setting_value="http://external-system-app:8000/get-users",
                    setting_description="Endpoint to fetch multiple users",
                    is_custom_setting=False
                ),
                "EXTERNAL_API_CONTEXT_IDENTIFIER_FIELD": Setting(
                    setting_basic_name="External API Context Identifier Field",
                    setting_value="user_id",  
                    setting_description="Field used to identify the user",
                    is_custom_setting=False
                ),
                "EXTERNAL_API_CONTEXT_CUSTOM_FIELDS": Setting(
                    setting_basic_name="External API Context Custom Fields",
                    setting_value="['custom_field1', 'custom_field2']",
                    setting_description="Supported custom fields",
                    is_custom_setting=False
                )
            },
            API_KEYS: {
                "EXTERNAL_SYSTEM_CLIENT_TOKEN": Setting(
                    setting_basic_name="External System Client Token",
                    setting_value="supersecretkey",
                    setting_description="Secret key for HMAC/JWT decoding",
                    is_custom_setting=False
                )
            },
            FRONTEND_SANDBOX_CHAT_INTERFACE: {
                "CHAT_CONTEXT_INTEGRATION_TYPE": Setting(
                    setting_basic_name="Chat Interface Integration Type",
                    setting_value="sql",
                    setting_description="Integration type for the Chat",
                    is_custom_setting=False
                ),
                "CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS": Setting(
                    setting_basic_name="Chat Interface Display Custom Fields",
                    setting_value="['role', 'is_admin', 'is_active']",
                    setting_description="Fields displayed on the UI",
                    is_custom_setting=False
                ),
                "CHAT_CONTEXT_DISPLAY_MAX_PAGINATION": Setting(
                    setting_basic_name="Chat Interface Display Pagination",
                    setting_value=10,
                    setting_description="Pagination limit",
                    is_custom_setting=False
                )
            }
        }
    )


class TestAPIContextIntegrationService:

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="SQLEXEC-71: Fix Skipped UT methods on TestAPIContextIntegrationService")
    async def test_call_external_get_user_endpoint_success(self):
        # Arrange
        tenant = get_mock_tenant()
        request = CreateExternalSessionRequest(context_user_identifier_value="user123")
        expected_response = {"field1": "value1", "field2": "value2"}
        fixed_timestamp = 1609459200

        mock_response = mock.AsyncMock()
        mock_response.status = 200
        mock_response.json = mock.AsyncMock(return_value=expected_response)

        mock_session_get = mock.AsyncMock()
        mock_session_get.return_value.__aenter__.return_value = mock_response
        mock_session_get.return_value.__aexit__.return_value = mock.AsyncMock()

        mock_session = mock.AsyncMock()
        mock_session.get = mock_session_get

        mock_client_session = mock.AsyncMock()
        mock_client_session.__aenter__.return_value = mock_session
        mock_client_session.__aexit__.return_value = mock.AsyncMock()

        with mock.patch(
            "api.core.services.external_system.api_context.api_context_integration_service.aiohttp.ClientSession",
            return_value=mock_client_session
        ):
            with mock.patch(
                "api.core.services.external_system.api_context.api_context_integration_service.time.time",
                return_value=fixed_timestamp
            ):
                # Act
                result = await APIContextIntegrationService.call_external_get_user_endpoint(tenant, request)

        # Assert
        assert result == expected_response
        mock_client_session.assert_called_once_with()
        mock_session.get.assert_called_once_with(
            "https://external.api/get-user?user_id=user123",
            headers={
                "Authorization": f"HMAC {hmac.new('supersecretkey'.encode(), 'user123:1609459200'.encode(), hashlib.sha256).hexdigest()}",
                "X-Timestamp": "1609459200"
            }
        )

    @pytest.mark.skip(reason="SQLEXEC-71: Fix Skipped UT methods on TestAPIContextIntegrationService")
    @pytest.mark.asyncio
    async def test_call_external_get_user_endpoint_non_200_response(self):
        # Arrange
        tenant = get_mock_tenant()
        request = CreateExternalSessionRequest(context_user_identifier_value="user123")
        error_response = {"detail": "Unauthorized"}

        mock_response = mock.AsyncMock()
        mock_response.status = 401
        mock_response.json = mock.AsyncMock(return_value=error_response)
        mock_response.text = mock.AsyncMock(return_value='{"detail": "Unauthorized"}')

        mock_session_get = mock.AsyncMock()
        mock_session_get.return_value.__aenter__.return_value = mock_response
        mock_session_get.return_value.__aexit__.return_value = mock.AsyncMock()

        mock_session = mock.AsyncMock()
        mock_session.get = mock_session_get

        mock_client_session = mock.AsyncMock()
        mock_client_session.__aenter__.return_value = mock_session
        mock_client_session.__aexit__.return_value = mock.AsyncMock()

        with mock.patch(
            "api.core.services.external_system.api_context.api_context_integration_service.aiohttp.ClientSession",
            return_value=mock_client_session
        ):
            with mock.patch(
                "api.core.services.external_system.api_context.api_context_integration_service.time.time",
                return_value=1609459200
            ):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    await APIContextIntegrationService.call_external_get_user_endpoint(tenant, request)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unauthorized"
        mock_client_session.assert_called_once_with()
        mock_session.get.assert_called_once_with(
            "https://external.api/get-user?user_id=user123",
            headers={
                "Authorization": f"HMAC {hmac.new('supersecretkey'.encode(), 'user123:1609459200'.encode(), hashlib.sha256).hexdigest()}",
                "X-Timestamp": "1609459200"
            }
        )

    @pytest.mark.skip(reason="SQLEXEC-71: Fix Skipped UT methods on TestAPIContextIntegrationService")
    @pytest.mark.asyncio
    async def test_call_external_get_user_endpoint_network_error(self):
        # Arrange
        tenant = get_mock_tenant()
        request = CreateExternalSessionRequest(context_user_identifier_value="user123")

        mock_session_get = mock.AsyncMock()
        mock_session_get.side_effect = aiohttp.ClientError("Connection failed")

        mock_session = mock.AsyncMock()
        mock_session.get = mock_session_get

        mock_client_session = mock.AsyncMock()
        mock_client_session.__aenter__.return_value = mock_session
        mock_client_session.__aexit__.return_value = mock.AsyncMock()

        with mock.patch(
            "api.core.services.external_system.api_context.api_context_integration_service.aiohttp.ClientSession",
            return_value=mock_client_session
        ):
            with mock.patch(
                "api.core.services.external_system.api_context.api_context_integration_service.time.time",
                return_value=1609459200
            ):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    await APIContextIntegrationService.call_external_get_user_endpoint(tenant, request)

        assert exc_info.value.status_code == 502
        assert "External service unavailable: Connection failed" in exc_info.value.detail
        mock_client_session.assert_called_once_with()
        mock_session.get.assert_called_once_with(
            "https://external.api/get-user?user_id=user123",
            headers={
                "Authorization": f"HMAC {hmac.new('supersecretkey'.encode(), 'user123:1609459200'.encode(), hashlib.sha256).hexdigest()}",
                "X-Timestamp": "1609459200"
            }
        )

    @pytest.mark.asyncio
    async def test_call_external_get_user_endpoint_missing_settings(self):
        # Arrange
        tenant = Tenant(
            tenant_id="TENANT_TST2",
            tenant_name="Test Tenant 2",
            admins=[],
            settings={
                API_CONTEXT_INTEGRATION: {
                    "EXTERNAL_API_CONTEXT_IDENTIFIER_FIELD": Setting(
                        setting_basic_name="External API Context Identifier Field",
                        setting_value="user_id",
                        setting_description="Field used to identify the user",
                        is_custom_setting=False
                    )
                },
                API_KEYS: {
                    "EXTERNAL_SYSTEM_CLIENT_TOKEN": Setting(
                        setting_basic_name="External System Client Token",
                        setting_value="supersecretkey",
                        setting_description="Client secret key for HMAC authentication",
                        is_custom_setting=False
                    )
                },
                EXTERNAL_JWT_AUTH_CATEGORY_KEY: {
                    "EXTERNAL_JWT_CUSTOM_FIELDS": Setting(
                        setting_basic_name="External JWT Custom Fields",
                        setting_value="['custom_field1', 'custom_field2']",
                        setting_description="Custom fields to extract from JWT",
                        is_custom_setting=False
                    ),
                    "EXTERNAL_JWT_USER_IDENTIFIER_FIELD": Setting(
                        setting_basic_name="External JWT User Identifier Field",
                        setting_value="sub",
                        setting_description="Field in JWT that identifies the user",
                        is_custom_setting=False
                    ),
                    "EXTERNAL_JWT_SECRET_KEY": Setting(
                        setting_basic_name="External JWT Secret Key",
                        setting_value="jwtsecretkey",
                        setting_description="Secret key to decode JWT",
                        is_custom_setting=False
                    )
                }
            }
        )
        request = CreateExternalSessionRequest(context_user_identifier_value="user123")

        with pytest.raises(ValueError, match="Get-user endpoint is not defined for the tenant."):
            await APIContextIntegrationService.call_external_get_user_endpoint(tenant, request)

    def test_decode_json_token_success(self):
        # Arrange
        tenant = get_mock_tenant()
        fixed_exp_time = time.time() + 3600
        user_token = {
            "access_token": jwt.encode(
                {
                    "user_id": "user123",
                    "custom_field1": "value1",
                    "custom_field2": "value2",
                    "exp": fixed_exp_time
                },
                "supersecretkey",
                algorithm="HS256"
            )
        }
        # Act
        result = APIContextIntegrationService.decode_json_token(tenant, user_token)
        # Assert
        assert isinstance(result, DecodedJwtToken)
        assert result.tenant_id == tenant.tenant_id
        assert result.custom_fields == {"custom_field1": "value1", "custom_field2": "value2"}
        assert result.user_identifier == "user123"
        expected_expiration = datetime.fromtimestamp(fixed_exp_time, tz=timezone.utc).isoformat()
        assert abs(datetime.fromisoformat(result.expiration).timestamp() - fixed_exp_time) < 5

    def test_decode_json_token_missing_access_token(self):
        # Arrange
        tenant = get_mock_tenant()
        user_token = {}
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            APIContextIntegrationService.decode_json_token(tenant, user_token)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Access token is missing in the user token."

    def test_decode_json_token_missing_jwt_settings(self):
        # Arrange
        tenant = Tenant(
            tenant_id="TENANT_TST3",
            tenant_name="Test Tenant 3",
            admins=[],
            settings={
                EXTERNAL_JWT_AUTH_CATEGORY_KEY: {
                    "EXTERNAL_JWT_CUSTOM_FIELDS": Setting(
                        setting_basic_name="External JWT Custom Fields",
                        setting_value="['custom_field1', 'custom_field2']",
                        setting_description="Custom fields to extract from JWT",
                        is_custom_setting=False
                    )
                    # Missing "EXTERNAL_JWT_USER_IDENTIFIER_FIELD" and "EXTERNAL_JWT_SECRET_KEY"
                }
            }
        )
        user_token = {"access_token": "somejwttoken"}
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            APIContextIntegrationService.decode_json_token(tenant, user_token)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Required JWT settings are missing or incomplete."

    def test_decode_json_token_expired_token(self):
        # Arrange
        tenant = get_mock_tenant()
        expired_time = time.time() - 3600
        user_token = {
            "access_token": jwt.encode(
                {
                    "user_id": "user123",
                    "custom_field1": "value1",
                    "custom_field2": "value2",
                    "exp": expired_time
                },
                "supersecretkey",
                algorithm="HS256"
            )
        }
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            APIContextIntegrationService.decode_json_token(tenant, user_token)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Token has expired."

    def test_decode_json_token_invalid_token(self):
        # Arrange
        tenant = get_mock_tenant()
        user_token = {"access_token": "invalidtoken"}
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            APIContextIntegrationService.decode_json_token(tenant, user_token)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid Token."

    def test_decode_json_token_missing_user_identifier(self):
        # Arrange
        tenant = get_mock_tenant()
        user_token = {
            "access_token": jwt.encode(
                {
                    "custom_field1": "value1",
                    "custom_field2": "value2",
                    "exp": time.time() + 3600
                },
                "supersecretkey",
                algorithm="HS256"
            )
        }
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            APIContextIntegrationService.decode_json_token(tenant, user_token)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User identifier field 'user_id' is missing in the token."

    def test_decode_json_token_missing_custom_fields(self):
        # Arrange
        tenant = get_mock_tenant()
        user_token = {
            "access_token": jwt.encode(
                {
                    "user_id": "user123",
                    "exp": time.time() + 3600
                },
                "supersecretkey",
                algorithm="HS256"
            )
        }
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            APIContextIntegrationService.decode_json_token(tenant, user_token)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "None of the custom fields ['custom_field1', 'custom_field2'] were found in the token."
