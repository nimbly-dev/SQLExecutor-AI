import pytest
import pymongo
from unittest import mock
from uuid import UUID
from fastapi import HTTPException
from api.core.services.authentication.session_manager_service import SessionManagerService
from model.decoded_jwt_token import DecodedJwtToken
from model.session_data import SessionData
from utils.database import mongodb


class TestSessionManagerService:
    @pytest.mark.asyncio
    async def test_create_jwt_session_success(self):
        # Arrange
        mock_collection = mock.AsyncMock()
        with mock.patch.object(mongodb, "db", { "sessions": mock_collection }):
            decoded_token = DecodedJwtToken(
                tenant_id="TENANT_TST1",
                custom_fields={"roles": ["admin"]},
                user_identifier="test_user",
                expiration="2024-12-15T08:00:00+00:00",
            )

            # Act
            result = await SessionManagerService.create_jwt_session(decoded_token)

            # Assert
            assert isinstance(result, SessionData)
            assert result.tenant_id == decoded_token.tenant_id
            assert result.user_id == decoded_token.user_identifier
            mock_collection.insert_one.assert_called_once_with(result.dict())

    @pytest.mark.asyncio
    async def test_create_jwt_session_failure(self):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_collection.insert_one.side_effect = Exception("Database error")
        with mock.patch.object(mongodb, "db", { "sessions": mock_collection }):
            decoded_token = DecodedJwtToken(
                tenant_id="TENANT_TST1",
                custom_fields={"roles": ["admin"]},
                user_identifier="test_user",
                expiration="2024-12-15T08:00:00+00:00",
            )

            # Act and Assert
            with pytest.raises(ValueError, match="Failed to create session: Database error"):
                await SessionManagerService.create_jwt_session(decoded_token)
            mock_collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_jwt_session_success(self):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_collection.delete_one.return_value.deleted_count = 1
        with mock.patch.object(mongodb, "db", { "sessions": mock_collection }):
            session_id = "f89d6854-d60d-477d-b211-a4d10f9a21a2"

            # Act
            result = await SessionManagerService.delete_jwt_session(session_id)

            # Assert
            assert result["message"] == "Successfully logged out"
            mock_collection.delete_one.assert_called_once_with({"session_id": UUID(session_id)})

    @pytest.mark.asyncio
    async def test_delete_jwt_session_not_found(self):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_collection.delete_one.return_value.deleted_count = 0
        with mock.patch.object(mongodb, "db", { "sessions": mock_collection }):
            session_id = "f89d6854-d60d-477d-b211-a4d10f9a21a2"

            # Act and Assert
            with pytest.raises(HTTPException) as excinfo:
                await SessionManagerService.delete_jwt_session(session_id)
            assert excinfo.value.status_code == 404
            assert excinfo.value.detail == "Session not found"
            mock_collection.delete_one.assert_called_once_with({"session_id": UUID(session_id)})

    @pytest.mark.asyncio
    async def test_create_jwt_session_failure(self):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_collection.insert_one.side_effect = pymongo.errors.PyMongoError("Database error")
        with mock.patch.object(mongodb, "db", {"sessions": mock_collection}):
            decoded_token = DecodedJwtToken(
                tenant_id="TENANT_TST1",
                custom_fields={"roles": ["admin"]},
                user_identifier="test_user",
                expiration="2024-12-15T08:00:00+00:00",
            )

            # Act and Assert
            with pytest.raises(ValueError, match="Failed to create session: Database error"):
                await SessionManagerService.create_jwt_session(decoded_token)
            mock_collection.insert_one.assert_called_once()