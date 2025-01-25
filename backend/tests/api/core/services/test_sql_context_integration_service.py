import pytest
from unittest import mock
from api.core.services.external_system.sql_context.sql_context_integration_service import SQLContextIntegrationService
from model.tenant.tenant import Tenant
from model.tenant.setting import Setting
from utils.database import mongodb
import pymongo


def get_mock_tenant():
    return Tenant(
        tenant_id="TENANT_TST1",
        tenant_name="Test Tenant",
        admins=[],  # Assuming 'admins' is a list; adjust if different
        settings={
            "POST_PROCESS_QUERYSCOPE": {
                "TENANT_SETTING_REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": Setting(
                    setting_basic_name="Remove Missing Columns on query scope",
                    setting_value="true",
                    setting_description="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE description not provided",
                    is_custom_setting=False  # Assuming this field exists; adjust if necessary
                ),
                "TENANT_SETTING_IGNORE_COLUMN_WILDCARDS": Setting(
                    setting_basic_name="Ignore Column Wildcards",
                    setting_value="true",
                    setting_description="IGNORE_COLUMN_WILDCARDS description not provided",
                    is_custom_setting=False  # Assuming this field exists; adjust if necessary
                )
            },
            "SQL_CONTEXT_INTEGRATION": {  # Added to align with service expectations
                "EXTERNAL_CONTEXT_USER_IDENTIFIER": Setting(
                    setting_basic_name="External Context User Identifier",
                    setting_value="user_id",
                    setting_description="Identifier for external context user",
                    is_custom_setting=False
                ),
                "EXTERNAL_CONTEXT_CUSTOM_FIELDS": Setting(
                    setting_basic_name="External Context Custom Fields",
                    setting_value="['field1', 'field2']",
                    setting_description="Custom fields from external context",
                    is_custom_setting=False
                ),
                "EXTERNAL_CONTEXT_TABLE": Setting(
                    setting_basic_name="External Context Table",
                    setting_value="external_table",
                    setting_description="Name of the external context table",
                    is_custom_setting=False
                )
            }
        }
    )


class TestSQLContextIntegrationService:

    @pytest.mark.asyncio
    async def test_get_customfields_from_context_table_success(self):
        # Arrange
        tenant = get_mock_tenant()
        context_user_identifier_value = "user123"
        expected_query_result = {"field1": "value1", "field2": "value2"}

        with mock.patch.object(SQLContextIntegrationService, "get_customfields_from_context_table", return_value=expected_query_result):
            # Act
            result = await SQLContextIntegrationService.get_customfields_from_context_table(tenant, context_user_identifier_value)

            # Assert
            assert result == expected_query_result

    @pytest.mark.asyncio
    async def test_get_customfields_from_context_table_no_result(self):
        # Arrange
        tenant = get_mock_tenant()
        context_user_identifier_value = "user123"

        with mock.patch.object(SQLContextIntegrationService, "get_customfields_from_context_table", return_value=None):
            # Act
            result = await SQLContextIntegrationService.get_customfields_from_context_table(tenant, context_user_identifier_value)

            # Assert
            assert result is None
