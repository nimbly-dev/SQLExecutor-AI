import pytest
from unittest import mock
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timezone, timedelta
from utils.database import mongodb
from utils.jwt_utils import authenticate_session, validate_api_key
from model.tenant import Tenant, Setting

class TestJWTUtils:

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_authenticate_session_success(self, mock_db):
        # Arrange
        session_id = "5b74630b-41ec-44f4-9818-6958bb2b3162"
        session_data = {
            "session_id": UUID(session_id),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
            "tenant_id": "tenant1",
            "user_id": "user1",
        }
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = session_data

        # Act
        result = await authenticate_session(x_session_id=session_id)

        # Assert
        assert result == session_data
        mock_collection.find_one.assert_called_once_with({"session_id": UUID(session_id)})

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_authenticate_session_expired(self, mock_db):
        # Arrange
        session_id = "5b74630b-41ec-44f4-9818-6958bb2b3162"
        session_data = {
            "session_id": UUID(session_id),
            "expires_at": datetime.now(timezone.utc) - timedelta(minutes=10),
            "tenant_id": "tenant1",
            "user_id": "user1",
        }
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = session_data

        # Act
        with pytest.raises(HTTPException) as excinfo:
            await authenticate_session(x_session_id=session_id)

        # Assert
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Session has expired"

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_validate_api_key_success(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        api_key = "valid_api_key"
        tenant_data = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",  
            "settings": {
                "TENANT_APPLICATION_TOKEN": {
                    "setting_basic_name": "Tenant SQLExecutor Application Token",
                    "setting_value": api_key,
                    "setting_category": "EXTERNAL_JWT_AUTH",
                    "is_custom_setting": False,
                }
            },
        }
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = tenant_data

        # Act
        result = await validate_api_key(x_api_key=api_key, tenant_id=tenant_id)

        # Assert
        assert result is None
        mock_collection.find_one.assert_called_once_with({"tenant_id": tenant_id})

    @pytest.mark.asyncio
    @mock.patch("utils.database.mongodb.db")
    async def test_validate_api_key_invalid(self, mock_db):
        # Arrange
        tenant_id = "tenant1"
        api_key = "invalid_api_key"
        tenant_data = {
            "tenant_id": tenant_id,
            "tenant_name": "Test Tenant",  
            "settings": {
                "TENANT_APPLICATION_TOKEN": {
                    "setting_basic_name": "Tenant SQLExecutor Application Token",
                    "setting_value": "valid_api_key",
                    "setting_category": "EXTERNAL_JWT_AUTH",
                    "is_custom_setting": False,
                }
            },
        }
        mock_collection = mock.AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find_one.return_value = tenant_data

        # Act
        with pytest.raises(HTTPException) as excinfo:
            await validate_api_key(x_api_key=api_key, tenant_id=tenant_id)

        # Assert
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "Invalid API Key"
