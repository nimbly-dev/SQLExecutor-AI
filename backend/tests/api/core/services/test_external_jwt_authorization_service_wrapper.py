import pytest
import jwt
from unittest import mock
from api.core.services.authentication.external_jwt_authentication_service_wrapper import ExternalJWTAuthorizationServiceWrapper
from model.requests.authentication.auth_login_request import AuthLoginRequest
from model.tenant import Tenant
from model.setting import Setting
from model.decoded_jwt_token import DecodedJwtToken
from jwt import ExpiredSignatureError, InvalidTokenError
from api.core.constants.tenant.settings_categories import EXTERNAL_JWT_AUTH_CATEGORY_KEY
from utils.tenant_manager.setting_utils import SettingUtils
from datetime import datetime, timezone

class TestExternalJWTAuthorizationServiceWrapper:

    def init_mock_tenant(self, tenant_id, category_key, settings):
        mock_settings = {
            category_key: {
                key: Setting(
                    setting_description=value.get("setting_description", ""),
                    setting_basic_name=value.get("setting_basic_name", key),
                    setting_default_value=value.get("setting_default_value"),
                    setting_value=value.get("setting_value"),
                    is_custom_setting=value.get("is_custom_setting", False)
                ) for key, value in settings.items()
            }
        }
        return Tenant(tenant_id=tenant_id, tenant_name="Test Tenant", settings=mock_settings)

    @pytest.mark.skip(reason="SQLEXEC-23: Skipping temporarily as this UT is complex and takes much time")
    @pytest.mark.asyncio
    @mock.patch("aiohttp.ClientSession")
    async def test_call_external_login_success(self, mock_client_session):
        tenant_id = "tenant123"
        auth_request = AuthLoginRequest(
            auth_field="test_user",
            auth_passkey_field="test_password",
            auth_tenant_id=tenant_id
        )

        settings = {
            "EXTERNAL_JWT_LOGIN_ENDPOINT": {"setting_value": "http://mock-service/login"},
            "EXTERNAL_JWT_AUTH_FIELD": {"setting_value": "username"},
            "EXTERNAL_JWT_AUTH_PASSKEY_FIELD": {"setting_value": "password"},
        }
        mock_tenant = self.init_mock_tenant(tenant_id, EXTERNAL_JWT_AUTH_CATEGORY_KEY, settings)

        # Mocked response
        mock_response = mock.AsyncMock()
        mock_response.status = 200
        mock_response.json = mock.AsyncMock(return_value={"access_token": "mock_token"})

        # Mocked context manager returned by session.post(...)
        mock_post_cm = mock.AsyncMock()
        mock_post_cm.__aenter__.return_value = mock_response
        mock_post_cm.__aexit__.return_value = None

        # Mock session
        mock_session = mock.AsyncMock()
        mock_session.post.return_value = mock_post_cm

        # Mock aiohttp.ClientSession()
        mock_client_session.return_value.__aenter__.return_value = mock_session
        mock_client_session.return_value.__aexit__.return_value = None

        # Call your method
        result = await ExternalJWTAuthorizationServiceWrapper.call_external_login(mock_tenant, auth_request)

        # Validate results
        assert result["access_token"] == "mock_token"
        mock_session.post.assert_called_once_with(
            "http://mock-service/login",
            json={"username": "test_user", "password": "test_password"},
        )


    @pytest.mark.asyncio
    async def test_call_external_login_missing_endpoint(self):
        tenant_id = "tenant123"
        auth_request = AuthLoginRequest(auth_field="test_user", auth_passkey_field="test_password", auth_tenant_id=tenant_id)

        settings = {
            "EXTERNAL_JWT_AUTH_FIELD": {"setting_value": "username"},
            "EXTERNAL_JWT_AUTH_PASSKEY_FIELD": {"setting_value": "password"}
        }

        mock_tenant = self.init_mock_tenant(tenant_id, EXTERNAL_JWT_AUTH_CATEGORY_KEY, settings)

        with pytest.raises(ValueError, match="Login endpoint is not defined for the tenant."):
            await ExternalJWTAuthorizationServiceWrapper.call_external_login(mock_tenant, auth_request)

    @mock.patch("jwt.decode")
    def test_decode_json_token_success(self, mock_jwt_decode):
        tenant_id = "tenant123"

        settings = {
            "EXTERNAL_JWT_CUSTOM_FIELDS": {"setting_value": "['roles']"},
            "EXTERNAL_JWT_USER_IDENTIFIER_FIELD": {"setting_value": "sub"},
            "EXTERNAL_JWT_SECRET_KEY": {"setting_value": "mock_secret"}
        }

        mock_tenant = self.init_mock_tenant(tenant_id, EXTERNAL_JWT_AUTH_CATEGORY_KEY, settings)

        user_token = {"access_token": "mock_token"}

        mock_jwt_decode.return_value = {
            "sub": "test_user",
            "roles": ["user"],
            "exp": datetime.now(tz=timezone.utc).timestamp(),
        }

        result = ExternalJWTAuthorizationServiceWrapper.decode_json_token(mock_tenant, user_token)

        assert isinstance(result, DecodedJwtToken)
        assert result.user_identifier == "test_user"
        assert result.custom_fields == {"roles": ["user"]}

        mock_jwt_decode.assert_called_once_with(
            b"mock_token", "mock_secret", algorithms=["HS256"]
        )
