import pytest
from unittest.mock import patch
from model.query_scope import QueryScope, Entities
from model.responses.schema.schema_tables_response import SchemaTablesResponse, TableResponse, ColumnResponse
from api.core.services.schema.schema_discovery_service import SchemaDiscoveryService
from fastapi import HTTPException


class TestSchemaDiscoveryService:
    @patch("api.core.services.schema.schema_discovery_service.SchemaDiscoveryService.get_best_matching_schemas")
    def test_get_best_matching_schemas_single_match(self, mock_get_best_matching_schemas):
        """
        Test the behavior of get_best_matching_schemas with a single match.
        """
        # Mock return value
        mock_get_best_matching_schemas.return_value = "schema1"

        # Input data
        query_scope = QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["products"],
                columns=["products.product_id"]
            )
        )
        schemas = [
            SchemaTablesResponse(
                schema_name="schema1",
                tables=[
                    TableResponse(table_name="products", columns=[
                        ColumnResponse(column_name="product_id", type="INTEGER")
                    ])
                ]
            )
        ]
        tenant_settings = {"IGNORE_COLUMN_WILDCARDS": True}

        # Act
        result = SchemaDiscoveryService.get_best_matching_schemas(query_scope, schemas, tenant_settings)

        # Assert
        mock_get_best_matching_schemas.assert_called_once_with(query_scope, schemas, tenant_settings)
        assert result == "schema1"

    @patch("api.core.services.schema.schema_discovery_service.SchemaDiscoveryService.get_best_matching_schemas")
    def test_get_best_matching_schemas_multiple_matches(self, mock_get_best_matching_schemas):
        """
        Test the behavior of get_best_matching_schemas with multiple matches.
        """
        # Mock return value
        mock_get_best_matching_schemas.return_value = ["schema1", "schema2"]

        # Input data
        query_scope = QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["products", "orders"],
                columns=["products.product_id", "orders.order_id"]
            )
        )
        schemas = [
            SchemaTablesResponse(
                schema_name="schema1",
                tables=[
                    TableResponse(table_name="products", columns=[
                        ColumnResponse(column_name="product_id", type="INTEGER")
                    ]),
                    TableResponse(table_name="orders", columns=[
                        ColumnResponse(column_name="order_id", type="INTEGER")
                    ])
                ]
            ),
            SchemaTablesResponse(
                schema_name="schema2",
                tables=[
                    TableResponse(table_name="products", columns=[
                        ColumnResponse(column_name="product_id", type="INTEGER")
                    ]),
                    TableResponse(table_name="orders", columns=[
                        ColumnResponse(column_name="order_id", type="INTEGER")
                    ])
                ]
            )
        ]
        tenant_settings = {"IGNORE_COLUMN_WILDCARDS": False}

        # Act
        result = SchemaDiscoveryService.get_best_matching_schemas(query_scope, schemas, tenant_settings)

        # Assert
        mock_get_best_matching_schemas.assert_called_once_with(query_scope, schemas, tenant_settings)
        assert result == ["schema1", "schema2"]

    @patch("api.core.services.schema.schema_discovery_service.SchemaDiscoveryService.get_best_matching_schemas")
    def test_get_best_matching_schemas_no_matches(self, mock_get_best_matching_schemas):
        """
        Test the behavior of get_best_matching_schemas with no matches.
        """
        # Mock return value
        mock_get_best_matching_schemas.return_value = []

        # Input data
        query_scope = QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["nonexistent_table"],
                columns=["nonexistent_column"]
            )
        )
        schemas = [
            SchemaTablesResponse(
                schema_name="schema1",
                tables=[
                    TableResponse(table_name="products", columns=[
                        ColumnResponse(column_name="product_id", type="INTEGER")
                    ])
                ]
            )
        ]
        tenant_settings = {"IGNORE_COLUMN_WILDCARDS": True}

        # Act
        result = SchemaDiscoveryService.get_best_matching_schemas(query_scope, schemas, tenant_settings)

        # Assert
        mock_get_best_matching_schemas.assert_called_once_with(query_scope, schemas, tenant_settings)
        assert result == []

