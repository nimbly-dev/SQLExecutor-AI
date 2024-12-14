import pytest
import jwt
from unittest import mock
from api.core.services.authentication.external_jwt_authentication_service_wrapper import ExternalJWTAuthorizationServiceWrapper
from model.requests.authentication.auth_login_request import AuthLoginRequest
from model.tenant import Tenant
from model.setting import Setting
from model.decoded_jwt_token import DecodedJwtToken
from jwt import ExpiredSignatureError, InvalidTokenError

class TestExternalJWTAuthorizationServiceWrapper:
    
    @pytest.mark.skip(reason="SQLEXEC-23: Skipping temporarily as this UT is complex and takes much time")
    @pytest.mark.asyncio
    @mock.patch("api.core.services.authentication.external_jwt_authentication_service_wrapper.TenantManagerService.get_tenant")
    @mock.patch("aiohttp.ClientSession")
    async def test_call_external_login_success(self, mock_client_session, mock_get_tenant):
        # Arrange
        tenant_id = "tenant123"
        auth_request = AuthLoginRequest(auth_field="test_user", auth_passkey_field="test_password")

        # Mock tenant settings
        mock_settings = {
            "EXTERNAL_JWT_LOGIN_ENDPOINT": Setting(
                setting_basic_name="External JWT Login Endpoint",
                setting_value="http://mock-service/login",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
            "EXTERNAL_JWT_AUTH_FIELD": Setting(
                setting_basic_name="External JWT Authentication Field",
                setting_value="username",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
            "EXTERNAL_JWT_AUTH_PASSKEY_FIELD": Setting(
                setting_basic_name="External JWT Passkey Field",
                setting_value="password",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
        }

        mock_tenant = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant",
            settings=mock_settings,
        )
        mock_get_tenant.return_value = mock_tenant

        # Mock aiohttp response
        mock_response = mock.AsyncMock()
        mock_response.status = 200
        mock_response.json = mock.AsyncMock(return_value={"access_token": "mock_token"})

        # Mock session.post to return the mocked response
        mock_post = mock.AsyncMock()
        mock_post.__aenter__.return_value = mock_response
        mock_post.__aexit__.return_value = mock.AsyncMock()

        # Mock session
        mock_session = mock.AsyncMock()
        mock_session.post.return_value = mock_post

        # Mock ClientSession to return the mocked session
        mock_client_session.return_value = mock_session

        # Act
        result = await ExternalJWTAuthorizationServiceWrapper.call_external_login(tenant_id, auth_request)

        # Assert
        assert result["access_token"] == "mock_token"
        mock_get_tenant.assert_called_once_with(tenant_id=tenant_id)
        mock_session.post.assert_called_once_with(
            "http://mock-service/login",
            json={"username": "test_user", "password": "test_password"},
        )
        
    @pytest.mark.asyncio
    @mock.patch("api.core.services.authentication.external_jwt_authentication_service_wrapper.TenantManagerService.get_tenant")
    async def test_call_external_login_missing_endpoint(self, mock_get_tenant):
        tenant_id = "tenant123"
        auth_request = AuthLoginRequest(
            auth_field="test_user",
            auth_passkey_field="test_password",
            auth_tenant_id=tenant_id
        )

        mock_settings = {
            "EXTERNAL_JWT_AUTH_FIELD": Setting(
                setting_basic_name="External JWT Authentication Field",
                setting_value="username",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
            "EXTERNAL_JWT_AUTH_PASSKEY_FIELD": Setting(
                setting_basic_name="External JWT Passkey Field",
                setting_value="password",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
        }

        mock_tenant = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant",
            settings=mock_settings,
        )
        mock_get_tenant.return_value = mock_tenant

        with pytest.raises(ValueError, match="Login endpoint is not defined for the tenant."):
            await ExternalJWTAuthorizationServiceWrapper.call_external_login(mock_tenant, auth_request)
        
    @pytest.mark.skip(reason="SQLEXEC-23: Skipping temporarily as this UT is complex and takes much time")
    @pytest.mark.asyncio
    @mock.patch("api.core.services.authentication.external_jwt_authentication_service_wrapper.TenantManagerService.get_tenant")
    @mock.patch("aiohttp.ClientSession")
    async def test_call_external_login_http_error(self, mock_client_session, mock_get_tenant):
        # Arrange
        tenant_id = "tenant123"
        auth_request = AuthLoginRequest(auth_field="test_user", auth_passkey_field="test_password")

        # Mock tenant settings
        mock_settings = {
            "EXTERNAL_JWT_LOGIN_ENDPOINT": Setting(
                setting_basic_name="External JWT Login Endpoint",
                setting_value="http://mock-service/login",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
            "EXTERNAL_JWT_AUTH_FIELD": Setting(
                setting_basic_name="External JWT Authentication Field",
                setting_value="username",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
            "EXTERNAL_JWT_AUTH_PASSKEY_FIELD": Setting(
                setting_basic_name="External JWT Passkey Field",
                setting_value="password",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
        }

        mock_tenant = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant",
            settings=mock_settings,
        )
        mock_get_tenant.return_value = mock_tenant

        # Mock aiohttp ClientSession
        mock_response = mock.AsyncMock()
        mock_response.status = 400
        mock_response.json.return_value = {"error": "Bad Request"}

        mock_post = mock.AsyncMock()
        mock_post.__aenter__.return_value = mock_response

        # Mock session.post to return the mock_post object
        mock_session = mock.AsyncMock()
        mock_session.post.return_value = mock_post

        # Mock the ClientSession itself to return the mock_session
        mock_client_session.return_value.__aenter__.return_value = mock_session

        # Act & Assert
        with pytest.raises(ValueError, match="Login failed with status code: 400"):
            await ExternalJWTAuthorizationServiceWrapper.call_external_login(tenant_id, auth_request)

    @pytest.mark.asyncio
    @mock.patch("api.core.services.authentication.external_jwt_authentication_service_wrapper.TenantManagerService.get_tenant")
    @mock.patch("aiohttp.ClientSession")
    async def test_call_external_login_exception_handling(self, mock_client_session, mock_get_tenant):
        tenant_id = "tenant123"
        auth_request = AuthLoginRequest(
            auth_field="test_user",
            auth_passkey_field="test_password",
            auth_tenant_id=tenant_id
        )

        mock_settings = {
            "EXTERNAL_JWT_LOGIN_ENDPOINT": Setting(
                setting_basic_name="External JWT Login Endpoint",
                setting_value="http://mock-service/login",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
            "EXTERNAL_JWT_AUTH_FIELD": Setting(
                setting_basic_name="External JWT Authentication Field",
                setting_value="username",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
            "EXTERNAL_JWT_AUTH_PASSKEY_FIELD": Setting(
                setting_basic_name="External JWT Passkey Field",
                setting_value="password",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False
            ),
        }

        mock_tenant = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant",
            settings=mock_settings,
        )
        mock_get_tenant.return_value = mock_tenant

        mock_session = mock.MagicMock()
        mock_client_session.return_value.__aenter__.return_value = mock_session
        mock_session.post.side_effect = Exception("Connection error")

        with pytest.raises(ValueError, match="An error occurred during login: Connection error"):
            await ExternalJWTAuthorizationServiceWrapper.call_external_login(mock_tenant, auth_request)


    @mock.patch("jwt.decode")
    @pytest.mark.skip(reason="SQLEXEC-23: Skipping temporarily as this UT is complex and takes much time")
    def test_decode_json_token_success(self, mock_jwt_decode):
        tenant_id = "tenant123"
        mock_settings = {
            "EXTERNAL_JWT_CUSTOM_FIELDS": Setting(
                setting_basic_name="External JWT Custom Fields",
                setting_value="['roles']",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
            "EXTERNAL_JWT_USER_IDENTIFIER_FIELD": Setting(
                setting_basic_name="External JWT User Identifier Field",
                setting_value="sub",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
            "EXTERNAL_JWT_SECRET_KEY": Setting(
                setting_basic_name="External JWT Secret Key",
                setting_value="mock_secret",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
        }

        mock_tenant = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant",
            settings=mock_settings,
        )

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
        assert isinstance(result.expiration, datetime)
        assert result.expiration.tzinfo == timezone.utc

        mock_jwt_decode.assert_called_once_with(
            b"mock_token", "mock_secret", algorithms=["HS256"]
        )

    @mock.patch("jwt.decode", side_effect=jwt.ExpiredSignatureError)
    def test_decode_json_token_expired_token(self, mock_jwt_decode):
        tenant_id = "tenant123"
        mock_settings = {
            "EXTERNAL_JWT_CUSTOM_FIELDS": Setting(
                setting_basic_name="External JWT Custom Fields",
                setting_value="['roles']",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
            "EXTERNAL_JWT_USER_IDENTIFIER_FIELD": Setting(
                setting_basic_name="External JWT User Identifier Field",
                setting_value="sub",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
            "EXTERNAL_JWT_SECRET_KEY": Setting(
                setting_basic_name="External JWT Secret Key",
                setting_value="mock_secret",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
        }

        mock_tenant = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant",
            settings=mock_settings,
        )

        user_token = {"access_token": "mock_token"}

        with pytest.raises(ValueError, match="Token has expired."):
            ExternalJWTAuthorizationServiceWrapper.decode_json_token(mock_tenant, user_token)

    @mock.patch("jwt.decode", side_effect=jwt.InvalidTokenError("Invalid signature"))
    def test_decode_json_token_invalid_token(self, mock_jwt_decode):
        tenant_id = "tenant123"
        mock_settings = {
            "EXTERNAL_JWT_CUSTOM_FIELDS": Setting(
                setting_basic_name="External JWT Custom Fields",
                setting_value="['roles']",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
            "EXTERNAL_JWT_USER_IDENTIFIER_FIELD": Setting(
                setting_basic_name="External JWT User Identifier Field",
                setting_value="sub",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
            "EXTERNAL_JWT_SECRET_KEY": Setting(
                setting_basic_name="External JWT Secret Key",
                setting_value="mock_secret",
                setting_category="EXTERNAL_JWT_AUTH",
                is_custom_setting=False,
            ),
        }

        mock_tenant = Tenant(
            tenant_id=tenant_id,
            tenant_name="Test Tenant",
            settings=mock_settings,
        )

        user_token = {"access_token": "mock_token"}

        with pytest.raises(ValueError, match="Invalid token: Invalid signature"):
            ExternalJWTAuthorizationServiceWrapper.decode_json_token(mock_tenant, user_token)