import pytest
from typing import List
from unittest import mock
from model.query_scope.query_scope import QueryScope, Entities
from model.responses.schema.schema_tables_response import SchemaTablesResponse, TableResponse
from utils.query_scope.validate_query_scope_utils import ValidateQueryScopeUtils

class TestValidateQueryScopeUtils:
    @pytest.fixture
    def sample_schemas(self) -> List[SchemaTablesResponse]:
        """
        Returns a sample list of SchemaTablesResponse objects for testing.
        """
        return [
            SchemaTablesResponse(
                schema_name="schema1",
                tables=[
                    TableResponse(table_name="products", columns=[]),
                    TableResponse(table_name="categories", columns=[]),
                ]
            ),
            SchemaTablesResponse(
                schema_name="schema2",
                tables=[
                    TableResponse(table_name="orders", columns=[]),
                    TableResponse(table_name="customers", columns=[]),
                ]
            )
        ]

    @pytest.fixture
    def sample_query_scope(self) -> QueryScope:
        """
        Returns a sample QueryScope object for testing.
        """
        return QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["products", "orders"],
                columns=[]
            )
        )

    @pytest.fixture
    def sample_query_scope_invalid(self) -> QueryScope:
        """
        Returns a QueryScope object with invalid table names for testing.
        """
        return QueryScope(
            intent="fetch_data",
            entities=Entities(
                tables=["non_existing_table"],
                columns=[]
            )
        )

    @pytest.mark.parametrize(
        "query_scope_fixture, expected",
        [
            ("sample_query_scope", True),  # Valid tables
            ("sample_query_scope_invalid", False),  # Invalid table
        ]
    )
    def test_validate_tables_exist_in_schemas(self, query_scope_fixture, expected, sample_schemas, request):
        """
        Tests the validate_tables_exist_in_schemas method.
        """
        query_scope = request.getfixturevalue(query_scope_fixture)

        # Act
        result = ValidateQueryScopeUtils.validate_tables_exist_in_schemas(sample_schemas, query_scope)

        # Assert
        assert result == expected
