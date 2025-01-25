# tests/api/core/services/test_sql_runner_service.py

import pytest
from unittest import mock
from sqlalchemy.exc import SQLAlchemyError
from api.core.services.sql_runner.sql_runner_service import SqlRunnerService
from model.tenant.tenant import Tenant, Setting
from utils.tenant_manager.setting_utils import SettingUtils
from utils.external_system_utils.external_system_db_utils import build_db_url
from api.core.constants.tenant.settings_categories import EXTERNAL_SYSTEM_DB_SETTING  # Ensure correct import


class TestSqlRunnerService:
    
    def init_mock_tenant(self, flavor: str, db_url: str) -> Tenant:
        return Tenant(
            tenant_id="TENANT_TST2",
            tenant_name="Test Tenant",
            admins=[],  # Assuming 'admins' is a list; adjust if different
            settings={
                EXTERNAL_SYSTEM_DB_SETTING: {  # Use the correct category key
                    "EXTERNAL_TENANT_DB_DIALECT": Setting(
                        setting_basic_name="EXTERNAL_TENANT_DB_DIALECT",
                        setting_value=flavor,
                        setting_description="SQL dialect for the external tenant DB",
                        is_custom_setting=False
                    ),
                    "EXTERNAL_SYSTEM_DB_CONNECTION_URL": Setting(
                        setting_basic_name="EXTERNAL_SYSTEM_DB_CONNECTION_URL",
                        setting_value=db_url,
                        setting_description="Connection URL for the external system DB",
                        is_custom_setting=False
                    )
                }
            }
        )
    
    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    @mock.patch("api.core.services.sql_runner.sql_runner_service.build_db_url")
    def test_run_sql_postgres_success(self, mock_build_db_url, mock_create_engine):
        # Arrange
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine

        # The object returned by __enter__ is what 'with engine.connect() as connection' binds to
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        # Configure your row mocks
        mock_connection.execute.return_value = [
            mock.Mock(_mapping={"user_id": 1, "username": "test_user"})
        ]

        tenant = self.init_mock_tenant("postgresql", "postgresql://user:pass@localhost/db")
        query = "SELECT * FROM users;"
        params = {}
        mock_build_db_url.return_value = "postgresql://user:pass@localhost/db"

        # Act
        result = SqlRunnerService.run_sql(query, tenant, params)

        # Assert
        assert result == [{"user_id": 1, "username": "test_user"}]
        mock_create_engine.assert_called_once_with("postgresql://user:pass@localhost/db", pool_size=10, max_overflow=20)
        mock_connection.execute.assert_called_once_with(mock.ANY, params)

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    @mock.patch("api.core.services.sql_runner.sql_runner_service.build_db_url")
    def test_run_sql_mysql_success(self, mock_build_db_url, mock_create_engine):
        # Arrange
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_connection.execute.return_value = [
            mock.Mock(_mapping={"user_id": 2, "username": "mysql_user"})
        ]

        tenant = self.init_mock_tenant("mysql", "mysql+pymysql://user:pass@localhost/db")
        query = "SELECT * FROM users;"
        params = {}
        mock_build_db_url.return_value = "mysql+pymysql://user:pass@localhost/db"

        # Act
        result = SqlRunnerService.run_sql(query, tenant, params)

        # Assert
        assert result == [{"user_id": 2, "username": "mysql_user"}]
        mock_create_engine.assert_called_once_with("mysql+pymysql://user:pass@localhost/db", pool_size=10, max_overflow=20)
        mock_connection.execute.assert_called_once_with(mock.ANY, params)

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    @mock.patch("api.core.services.sql_runner.sql_runner_service.build_db_url")
    def test_run_sql_sqlite_success(self, mock_build_db_url, mock_create_engine):
        # Arrange
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_connection.execute.return_value = [
            mock.Mock(_mapping={"user_id": 3, "username": "sqlite_user"})
        ]

        tenant = self.init_mock_tenant("sqlite", "sqlite:///:memory:")
        query = "SELECT * FROM users;"
        params = {}
        mock_build_db_url.return_value = "sqlite:///:memory:"

        # Act
        result = SqlRunnerService.run_sql(query, tenant, params)

        # Assert
        assert result == [{"user_id": 3, "username": "sqlite_user"}]
        mock_create_engine.assert_called_once_with("sqlite:///:memory:")
        mock_connection.execute.assert_called_once_with(mock.ANY, params)

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    @mock.patch("api.core.services.sql_runner.sql_runner_service.build_db_url")
    def test_run_sql_query_failure(self, mock_build_db_url, mock_create_engine):
        # Arrange
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        mock_connection.execute.side_effect = SQLAlchemyError("Query failed")

        tenant = self.init_mock_tenant("postgresql", "postgresql://user:pass@localhost/db")
        query = "SELECT * FROM non_existent_table;"
        params = {}
        mock_build_db_url.return_value = "postgresql://user:pass@localhost/db"

        # Act
        result = SqlRunnerService.run_sql(query, tenant, params)

        # Assert
        assert "Query execution failed" in result
        mock_create_engine.assert_called_once_with("postgresql://user:pass@localhost/db", pool_size=10, max_overflow=20)
        mock_connection.execute.assert_called_once_with(mock.ANY, params)

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    @mock.patch("api.core.services.sql_runner.sql_runner_service.build_db_url")
    def test_run_sql_with_params(self, mock_build_db_url, mock_create_engine):
        # Arrange
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        mock_connection.execute.return_value = [
            mock.Mock(_mapping={"user_id": 1, "username": "test_user"})
        ]

        tenant = self.init_mock_tenant("sqlite", "sqlite:///:memory:")
        query = "SELECT * FROM users WHERE user_id = :id;"
        params = {"id": 1}
        mock_build_db_url.return_value = "sqlite:///:memory:"

        # Act
        result = SqlRunnerService.run_sql(query, tenant, params)

        # Assert
        assert result == [{"user_id": 1, "username": "test_user"}]
        mock_create_engine.assert_called_once_with("sqlite:///:memory:")
        mock_connection.execute.assert_called_once_with(mock.ANY, params)

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    @mock.patch("api.core.services.sql_runner.sql_runner_service.build_db_url")
    def test_run_sql_unsupported_flavor(self, mock_build_db_url, mock_create_engine):
        # Arrange
        tenant = self.init_mock_tenant("oracle", "oracle://user:pass@localhost/db")
        query = "SELECT * FROM users;"
        params = {}
        mock_build_db_url.return_value = "oracle://user:pass@localhost/db"

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported SQL flavor: oracle"):
            SqlRunnerService.run_sql(query, tenant, params)

        # Assert that create_engine was **not** called since flavor is unsupported
        mock_create_engine.assert_not_called()
