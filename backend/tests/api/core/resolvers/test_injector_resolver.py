import pytest
from unittest.mock import MagicMock
from app.api.core.resolvers.access_control.injector_resolver import InjectorResolver
from app.model.external_system_integration.external_user_session_data import ExternalSessionData
from app.model.tenant.setting import Setting
import uuid

class TestInjectorResolver:

    @pytest.fixture
    def mock_session(self):
        return ExternalSessionData(
            session_id=str(uuid.uuid4()),
            tenant_id="test_tenant",
            user_id="test_user",
            custom_fields={
                "role": "customer",
                "sub": "customer_user_1",
                "is_active": True
            },
            created_at="2024-12-30T13:05:17.415881+00:00",
            expires_at="2024-12-30T14:05:17+00:00",
            session_settings={}
        )

    @pytest.fixture
    def mock_ruleset(self):
        mock_ruleset = MagicMock()
        mock_ruleset.injectors = {
            "customer_scope": MagicMock(
                name="Customer Filter",
                enabled=True,
                condition=MagicMock(condition="${jwt.custom_fields.role} == 'customer'"),
                tables={
                    "users": MagicMock(filters="user_id = ${jwt.custom_fields.sub}")
                }
            )
        }
        mock_ruleset.conditions = {"is_customer": "${jwt.custom_fields.role} == 'customer'"}
        return mock_ruleset

    @pytest.fixture
    def mock_tenant(self):
        mock_tenant = MagicMock()
        mock_tenant.tenant_id = "test_tenant"
        mock_tenant.settings = {
            "SQL_INJECTORS": {
                "DYNAMIC_INJECTION": Setting(
                    setting_description="Dynamic Injection",
                    setting_basic_name="Dynamic Injection",
                    setting_value=True,  # Set as boolean
                    is_custom_setting=False
                )
            }
        }
        return mock_tenant

    def test_apply_injectors_with_dynamic_enabled(self, mock_session, mock_ruleset, mock_tenant):
        # Arrange
        resolver = InjectorResolver(mock_session, mock_ruleset)
        
        # Act
        sql_query, injector_str = resolver.apply_injectors("SELECT * FROM users", mock_tenant)
        
        # Assert
        assert "WHERE user_id = 'customer_user_1'" in sql_query
        assert injector_str == "user_id = 'customer_user_1'"

    @pytest.mark.skip(reason="SQLEXEC-32: Skipping temporarily as this UT is complex and takes much time")
    def test_apply_injectors_with_dynamic_disabled(self, mock_session, mock_ruleset, mock_tenant):
        # Arrange
        mock_tenant.settings["SQL_INJECTORS"]["DYNAMIC_INJECTION"].setting_value = False 
        resolver = InjectorResolver(mock_session, mock_ruleset)
        
        # Act
        sql_query, injector_str = resolver.apply_injectors("SELECT * FROM users WHERE id = 1", mock_tenant)
        
        # Assert
        assert "WHERE user_id = 'customer_user_1'" not in sql_query
        assert "WHERE id = 1" in sql_query
        assert injector_str is None

    def test_apply_injectors_no_injectors(self, mock_session, mock_tenant):
        # Arrange
        mock_ruleset = MagicMock()
        mock_ruleset.injectors = {}
        resolver = InjectorResolver(mock_session, mock_ruleset)
        
        # Act
        sql_query, injector_str = resolver.apply_injectors("SELECT * FROM users;", mock_tenant)
        
        # Assert
        assert sql_query == "SELECT * FROM users;"
        assert injector_str is None
