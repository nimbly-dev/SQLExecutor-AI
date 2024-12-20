from model.tenant import Tenant
from model.setting import Setting
from model.schema import Schema
from model.query_scope import QueryScope
from model.entities import Entities
from typing import List, Dict, Any, Union

class PostProcessQueryScopeSettingsUtils:
    
    @staticmethod
    def remove_missing_columns_from_query_scope(schema: Schema, query_scope: QueryScope) -> (QueryScope, List[str]):
        """
        Key: (IGNORE_MISSING_COLUMN_ON_QUERY_SCOPE) 
        Removes columns from query_scope that do not exist in the schema, except for wildcards.

        Args:
            schema (Schema): The schema object containing table and column information.
            query_scope (QueryScope): The query scope object defining the intent and entities.

        Returns:
            QueryScope: The updated query scope with missing columns removed.
            List[str]: List of missing columns for tracking.
        """
        tables = query_scope.entities.tables
        columns = query_scope.entities.columns

        # Build schema table map including synonyms
        schema_table_map = {table_name: table for table_name, table in schema.tables.items()}
        for table_name, table in schema.tables.items():
            for synonym in table.synonyms or []:
                schema_table_map[synonym] = table

        valid_columns = []
        missing_columns = []  # To track invalid columns, including invalid wildcards

        for column in columns:
            # Keep global wildcard as is
            if column == "*":
                valid_columns.append(column)
                continue

            # Handle table-specific wildcards (e.g., "table.*") and skip tracking
            if column.endswith(".*"):
                table_name = column.split(".*")[0]
                if table_name in schema_table_map:
                    valid_columns.append(column)  # Keep wildcard if the table exists
                else:
                    missing_columns.append(column)  # Track invalid wildcard
                continue

            # Handle specific table.column pairs
            if "." in column:
                table_name, column_name = column.split(".", 1)
                if table_name in schema_table_map:
                    table = schema_table_map[table_name]
                    if column_name in table.columns:
                        valid_columns.append(column)
                    else:
                        missing_columns.append(column)  # Track missing column
                else:
                    missing_columns.append(column)  # Track missing table.column
            else:
                missing_columns.append(column)  # Track completely invalid format

        # Update entities with valid columns
        updated_entities = Entities(
            tables=tables,
            columns=valid_columns
        )

        query_scope.entities = updated_entities
        return query_scope, missing_columns

