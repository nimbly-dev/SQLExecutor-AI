import pytest
from unittest import mock
from sqlalchemy.exc import SQLAlchemyError
from api.core.services.sql_runner.sql_runner_service import SqlRunnerService
from model.tenant.tenant import Tenant, Setting
from utils.tenant_manager.setting_utils import SettingUtils

class TestSqlRunnerService:
    
    def init_mock_tenant(self, flavor: str, db_url: str) -> Tenant:
        return Tenant(
            tenant_id="TENANT_TST2",
            tenant_name="Test Tenant",
            settings={
                "SQL_RUNNER": {
                    "SQL_FLAVOR": Setting(
                        setting_basic_name="SQL_FLAVOR",
                        setting_value=flavor,
                        is_custom_setting=False
                    ),
                    "EXTERNAL_SYSTEM_DB_CONNECTION_URL": Setting(
                        setting_basic_name="EXTERNAL_SYSTEM_DB_CONNECTION_URL",
                        setting_value=db_url,
                        is_custom_setting=False
                    )
                }
            }
        )

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    def test_run_sql_postgres_success(self, mock_create_engine):
        # Use MagicMock so that __enter__ and __exit__ exist:
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine

        # The object returned by __enter__ is what 'with engine.connect() as connection' binds to
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        # Configure your row mocks
        mock_connection.execute.return_value = [
            mock.Mock(_mapping={"user_id": 1, "username": "test_user"})
        ]

        # Arrange
        tenant = self.init_mock_tenant("postgres", "postgresql://user:pass@localhost/db")
        query = "SELECT * FROM users;"
        params = {}

        # Act
        result = SqlRunnerService.run_sql(query, tenant, params)

        # Assert
        assert result == [{"user_id": 1, "username": "test_user"}]
        mock_create_engine.assert_called_once()
        mock_connection.execute.assert_called_once()

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    def test_run_sql_mysql_success(self, mock_create_engine):
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

        result = SqlRunnerService.run_sql(query, tenant, params)

        assert result == [{"user_id": 2, "username": "mysql_user"}]
        mock_create_engine.assert_called_once()
        mock_connection.execute.assert_called_once()

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    def test_run_sql_query_failure(self, mock_create_engine):
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_connection = mock.MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        mock_connection.execute.side_effect = SQLAlchemyError("Query failed")

        tenant = self.init_mock_tenant("postgres", "postgresql://user:pass@localhost/db")
        query = "SELECT * FROM non_existent_table;"
        params = {}

        result = SqlRunnerService.run_sql(query, tenant, params)
        assert "Query execution failed" in result
        mock_create_engine.assert_called_once()
        mock_connection.execute.assert_called_once()

    @mock.patch("api.core.services.sql_runner.sql_runner_service.create_engine")
    def test_run_sql_with_params(self, mock_create_engine):
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

        result = SqlRunnerService.run_sql(query, tenant, params)

        assert result == [{"user_id": 1, "username": "test_user"}]
        mock_create_engine.assert_called_once()
        mock_connection.execute.assert_called_once_with(mock.ANY, params)
