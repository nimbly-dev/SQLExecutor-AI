import pytest
import pymongo
from unittest import mock
from uuid import UUID
from fastapi import HTTPException
from api.core.services.authentication.session_manager_service import SessionManagerService
from model.authentication.decoded_jwt_token import DecodedJwtToken
from model.authentication.session_data import SessionData
from model.tenant.tenant import Tenant
from model.tenant.setting import Setting
from utils.database import mongodb


class TestSessionManagerService:
    
    @pytest.mark.asyncio
    async def test_create_jwt_session_success(self):
        # Arrange
        mock_collection = mock.AsyncMock()
        with mock.patch.object(mongodb, "db", {"sessions": mock_collection}):
            decoded_token = DecodedJwtToken(
                tenant_id="TENANT_TST1",
                custom_fields={"roles": ["admin"]},
                user_identifier="test_user",
                expiration="2024-12-15T08:00:00+00:00",
            )

            # Mock tenant with proper Setting objects
            tenant = Tenant(
                tenant_id="TENANT_TST1",
                tenant_name="Test Tenant",
                settings={
                    "POST_PROCESS_QUERYSCOPE": {
                        "TENANT_SETTING_REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": Setting(
                            setting_basic_name="Remove Missing Columns on query scope",
                            setting_value="true",
                            setting_description="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE description not provided"
                        ),
                        "TENANT_SETTING_IGNORE_COLUMN_WILDCARDS": Setting(
                            setting_basic_name="Ignore Column Wildcards",
                            setting_value="true",
                            setting_description="IGNORE_COLUMN_WILDCARDS description not provided"
                        )
                    }
                }
            )

            # Act
            result = await SessionManagerService.create_jwt_session(decoded_token, tenant)

            # Assert
            assert isinstance(result, SessionData)
            assert result.tenant_id == decoded_token.tenant_id
            assert result.user_id == decoded_token.user_identifier
            mock_collection.insert_one.assert_called_once_with(result.dict())

    @pytest.mark.skip(reason="SQLEXEC-32: Skipping temporarily as this UT is complex and takes much time")
    @pytest.mark.asyncio
    async def test_create_jwt_session_failure(self):
        # Arrange
        mock_collection = mock.AsyncMock()
        mock_collection.insert_one.side_effect = pymongo.errors.PyMongoError("Database error")

        with mock.patch.object(mongodb, "db", {"sessions": mock_collection}):
            # Create the decoded token
            decoded_token = DecodedJwtToken(
                tenant_id="TENANT_TST1",
                custom_fields={"roles": ["admin"]},
                user_identifier="test_user",
                expiration="2024-12-15T08:00:00+00:00",
            )

            # Mock tenant with proper Setting objects
            tenant = Tenant(
                tenant_id="TENANT_TST1",
                tenant_name="Test Tenant",
                settings={
                    "POST_PROCESS_QUERYSCOPE": {
                        "TENANT_SETTING_REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": Setting(
                            setting_basic_name="Remove Missing Columns on query scope",
                            setting_value="true",
                            setting_description="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE description not provided"
                        ),
                        "TENANT_SETTING_IGNORE_COLUMN_WILDCARDS": Setting(
                            setting_basic_name="Ignore Column Wildcards",
                            setting_value="true",
                            setting_description="IGNORE_COLUMN_WILDCARDS description not provided"
                        )
                    }
                }
            )

            # Act 
            with pytest.raises(ValueError, match="Failed to create session: Database error"):
                # Pass the tenant parameter here (FIX)
                await SessionManagerService.create_jwt_session(decoded_token, tenant)

            # Assert
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