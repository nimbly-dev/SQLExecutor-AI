import pytest
import bcrypt
from unittest import mock
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
from fastapi import HTTPException

from api.core.services.authentication.admin_authentication_service import AdminAuthenticationService
from utils.database import mongodb
from utils.jwt_utils import decode_jwt
from utils.tenant_manager.setting_utils import SettingUtils
from model.requests.authentication.auth_admin_login_request import AuthLoginRequest
from model.tenant.tenant import Tenant


@pytest.mark.asyncio
class TestAdminAuthenticationService:
    def _get_mock_tenant_data(self):
        """
        Returns a Tenant-like dict with hashed password so bcrypt.checkpw() doesn't fail.
        """
        correct_hashed_password = bcrypt.hashpw(
            b"correct_password", bcrypt.gensalt()
        ).decode("utf-8")

        return {
            "tenant_id": "mock_tenant_id",
            "tenant_name": "Mock Tenant",
            "admins": [
                {
                    "user_id": "admin_user_id",
                    "role": "admin",
                    "password": correct_hashed_password,
                }
            ],
            "settings": {
                "ADMIN_AUTH": {
                    "ADMIN_AUTH_TOKEN": {
                        "setting_basic_name": "ADMIN_AUTH_TOKEN",
                        "setting_value": "secret_key"
                    }
                }
            },
        }

    @pytest.fixture
    def mock_mongo_db(self):
        tenant_collection = AsyncMock()
        admin_session_collection = AsyncMock()
        mock_db = {
            "tenants": tenant_collection,
            "admin_sessions": admin_session_collection
        }
        with mock.patch.object(mongodb, 'db', mock_db):
            yield mock_db

    @pytest.mark.asyncio
    @mock.patch.object(SettingUtils, "get_setting_value", return_value="secret_key")
    @mock.patch.object(jwt, "encode", return_value="mock_jwt_token")
    async def test_login_admin_success(
        self, 
        mock_jwt_encode, 
        mock_setting_value, 
        mock_mongo_db
    ):
        #Arrange
        tenant_data = self._get_mock_tenant_data()
        mock_mongo_db["tenants"].find_one.return_value = tenant_data
        mock_mongo_db["admin_sessions"].insert_one.return_value = MagicMock()

        auth_request = AuthLoginRequest(
            tenant_id="mock_tenant_id",
            user_id="admin_user_id",
            password="correct_password"
        )

        #Act
        result = await AdminAuthenticationService.login_admin(auth_request)

        #Assert
        assert "JWT_TOKEN" in result
        assert result["JWT_TOKEN"] == "Bearer mock_jwt_token"
        mock_mongo_db["tenants"].find_one.assert_awaited_once()
        mock_mongo_db["admin_sessions"].insert_one.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_login_admin_tenant_not_found(self, mock_mongo_db):
        #Arrange
        auth_request = AuthLoginRequest(
            tenant_id="non_existent_tenant", 
            user_id="admin_user_id", 
            password="password"
        )
        mock_mongo_db["tenants"].find_one.return_value = None

        #Act / Assert
        with pytest.raises(HTTPException) as exc_info:
            await AdminAuthenticationService.login_admin(auth_request)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_login_admin_invalid_credentials(self, mock_mongo_db):
        """
        Use a valid hashed password for 'correct_password',
        but provide 'wrong_password' in AuthLoginRequest so the check fails.
        """
        tenant_data = self._get_mock_tenant_data()
        mock_mongo_db["tenants"].find_one.return_value = tenant_data

        auth_request = AuthLoginRequest(
            tenant_id="mock_tenant_id",
            user_id="admin_user_id",
            password="wrong_password"
        )

        with pytest.raises(HTTPException) as exc_info:
            await AdminAuthenticationService.login_admin(auth_request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @mock.patch.object(jwt, "decode")
    @mock.patch.object(decode_jwt, "__call__")
    async def test_logout_admin_successful(
        self, 
        mock_decode_jwt_call, 
        mock_jwt_decode, 
        mock_mongo_db
    ):
        #Arrange
        mock_token = "mock_token"
        mock_session_id = str(uuid4())
        payload = {
            "tenant_id": "mock_tenant_id",
            "session_id": mock_session_id
        }
        mock_jwt_decode.return_value = payload
        mock_decode_jwt_call.return_value = payload

        tenant_data = self._get_mock_tenant_data()
        mock_mongo_db["tenants"].find_one.return_value = tenant_data
        mock_mongo_db["admin_sessions"].delete_one.return_value = MagicMock(deleted_count=1)

        #Act
        result = await AdminAuthenticationService.logout_admin_from_token(mock_token)

        #Assert
        assert result["message"] == "Successfully logged out"
        mock_mongo_db["tenants"].find_one.assert_awaited_once()
        mock_mongo_db["admin_sessions"].delete_one.assert_awaited_once()

    @pytest.mark.asyncio
    @mock.patch.object(jwt, "decode")
    async def test_logout_admin_missing_tenant_id_in_token(self, mock_jwt_decode, mock_mongo_db):
        #Arrange
        mock_token = "mock_token"
        payload = {"session_id": str(uuid4())}
        mock_jwt_decode.return_value = payload

        #Act / Assert
        with pytest.raises(HTTPException) as exc_info:
            await AdminAuthenticationService.logout_admin_from_token(mock_token)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    @mock.patch.object(jwt, "decode")
    async def test_logout_admin_tenant_not_found(self, mock_jwt_decode, mock_mongo_db):
        #Arrange
        mock_token = "mock_token"
        payload = {"tenant_id": "non_existent_tenant", "session_id": str(uuid4())}
        mock_jwt_decode.return_value = payload
        mock_mongo_db["tenants"].find_one.return_value = None

        #Act / Assert
        with pytest.raises(HTTPException) as exc_info:
            await AdminAuthenticationService.logout_admin_from_token(mock_token)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @mock.patch.object(jwt, "decode")
    @mock.patch.object(decode_jwt, "__call__")
    async def test_logout_admin_session_not_found(
        self, 
        mock_decode_jwt_call, 
        mock_jwt_decode, 
        mock_mongo_db
    ):
        #Arrange
        mock_token = "mock_token"
        mock_session_id = str(uuid4())
        payload = {
            "tenant_id": "mock_tenant_id",
            "session_id": mock_session_id
        }
        mock_jwt_decode.return_value = payload
        mock_decode_jwt_call.return_value = payload

        tenant_data = self._get_mock_tenant_data()
        mock_mongo_db["tenants"].find_one.return_value = tenant_data
        mock_mongo_db["admin_sessions"].delete_one.return_value = MagicMock(deleted_count=0)

        #Act / Assert
        with pytest.raises(HTTPException) as exc_info:
            await AdminAuthenticationService.logout_admin_from_token(mock_token)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @mock.patch.object(jwt, "decode")
    @mock.patch.object(decode_jwt, "__call__")
    async def test_logout_admin_invalid_session_id(
        self,
        mock_decode_jwt_call, 
        mock_jwt_decode, 
        mock_mongo_db
    ):
        #Arrange
        mock_token = "mock_token"
        payload = {
            "tenant_id": "mock_tenant_id",
            "session_id": "not-a-valid-uuid"
        }
        mock_jwt_decode.return_value = payload
        mock_decode_jwt_call.return_value = payload

        tenant_data = self._get_mock_tenant_data()
        mock_mongo_db["tenants"].find_one.return_value = tenant_data

        #Act / Assert
        with pytest.raises(HTTPException) as exc_info:
            await AdminAuthenticationService.logout_admin_from_token(mock_token)
        assert exc_info.value.status_code == 400
