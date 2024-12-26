import pytest
from unittest import mock
from datetime import datetime, timezone
from uuid import uuid4
from model.schema.schema import Schema
from model.schema.column import Column
from model.schema.joins import Joins
from model.schema.table import Table
from model.query_scope.query_scope import QueryScope
from model.query_scope.entities import Entities
from model.tenant.tenant import Tenant
from model.authentication.external_user_session_data import ExternalSessionData
from model.authentication.external_user_session_data_setting import ExternalSessionDataSetting
from api.core.resolvers.schema.schema_resolver import SchemaResolver
from api.core.constants.tenant.settings_categories import SCHEMA_RESOLVER_CATEGORY_KEY
from utils.tenant_manager.setting_utils import SettingUtils

class TestSchemaResolver:

    def init_mock_tenant(self, tenant_id, category_key, settings):
        mock_settings = {
            category_key: {
                key: {
                    "setting_description": value.get("setting_description", ""),
                    "setting_basic_name": value.get("setting_basic_name", key),
                    "setting_value": value.get("setting_value"),
                    "is_custom_setting": value.get("is_custom_setting", False)
                } for key, value in settings.items()
            }
        }
        return Tenant(tenant_id=tenant_id, tenant_name="Test Tenant", settings=mock_settings)

    def init_mock_schema(self):
        return Schema(
            tenant_id="tenant123",
            schema_name="order_management",
            description="Schema for managing orders",
            exclude_description_on_generate_sql=False,
            tables={
                "orders": Table(
                    columns={
                        "order_id": Column(
                            type="INTEGER",
                            description="Primary key for orders",
                            constraints=["PRIMARY KEY"],
                            synonyms=[],
                            exclude_description_on_generate_sql=False,
                            is_sensitive_column=False
                        ),
                        "customer_id": Column(
                            type="INTEGER",
                            description="Customer ID",
                            constraints=["FOREIGN KEY"],
                            synonyms=[],
                            exclude_description_on_generate_sql=False,
                            is_sensitive_column=False
                        )
                    },
                    description="Orders table",
                    synonyms=["purchases", "transactions"],
                    relationships={
                        "customers": Joins(
                            description="Relationship with customers",
                            exclude_description_on_generate_sql=False,
                            table="customers",
                            on="orders.customer_id = customers.customer_id",
                            type="INNER"
                        )
                    },
                    exclude_description_on_generate_sql=False
                )
            }
        )

    @pytest.mark.asyncio
    async def test_resolve_schema(self):
        #Arrange
        session_data = ExternalSessionData(
            session_id=str(uuid4()),
            tenant_id="tenant123",
            user_id="user123",
            custom_fields={"roles": ["user"]},
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc)
        )

        settings = {
            "REMOVE_SENSITIVE_COLUMNS": {"setting_value": True},
            "REMOVE_ALL_DESCRIPTIONS": {"setting_value": False}
        }
        mock_tenant = self.init_mock_tenant("tenant123", SCHEMA_RESOLVER_CATEGORY_KEY, settings)

        query_scope = QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["orders"],
                columns=["orders.order_id", "orders.customer_id"]
            )
        )

        mock_schema = self.init_mock_schema()

        resolver = SchemaResolver(
            session_data=session_data,
            tenant=mock_tenant,
            matched_schema=mock_schema,
            query_scope=query_scope
        )

        #Act
        resolved_schema = resolver.resolve_schema()

        #Assert
        assert "orders" in resolved_schema["tables"]
        assert "order_id" in resolved_schema["tables"]["orders"]["columns"]
        assert "customer_id" in resolved_schema["tables"]["orders"]["columns"]
        assert "relationships" in resolved_schema["tables"]["orders"]
        assert "customers" in resolved_schema["tables"]["orders"]["relationships"]

    @pytest.mark.asyncio
    async def test_resolve_schema_remove_descriptions(self):
        #Arrange
        settings = {
            "REMOVE_SENSITIVE_COLUMNS": {"setting_value": False},
            "REMOVE_ALL_DESCRIPTIONS": {"setting_value": True}
        }
        mock_tenant = self.init_mock_tenant("tenant123", SCHEMA_RESOLVER_CATEGORY_KEY, settings)

        mock_schema = self.init_mock_schema()

        query_scope = QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["orders"],
                columns=["orders.order_id", "orders.customer_id"]
            )
        )

        resolver = SchemaResolver(
            session_data=ExternalSessionData(
                session_id=str(uuid4()),
                tenant_id="tenant123",
                user_id="user123",
                custom_fields={},
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc)
            ),
            tenant=mock_tenant,
            matched_schema=mock_schema,
            query_scope=query_scope
        )

        #Act
        resolved_schema = resolver.resolve_schema()

        #Assert
        assert "description" not in resolved_schema["tables"]["orders"]
        assert "description" not in resolved_schema["tables"]["orders"]["columns"]["order_id"]
        assert "description" not in resolved_schema["tables"]["orders"]["columns"]["customer_id"]
        assert "description" not in resolved_schema["tables"]["orders"]["relationships"]["customers"]
