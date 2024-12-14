from utils.database import mongodb
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from pymongo import ASCENDING
from typing import List, Dict, Union

from model.schema import Schema
from model.tenant import Tenant
from model.query_scope import QueryScope
from model.responses.schema.schema_tables_response import SchemaTablesResponse

class SchemaDiscoveryService:
                
    @staticmethod
    def get_best_matching_schemas(query_scope: QueryScope, schemas: List[SchemaTablesResponse], tenant_settings: Dict) -> Union[str, List[str]]:
        """
        Matches the provided query scope to the most relevant schemas for a tenant.

        How it Works:
        - The method matches the tables and columns in the `query_scope` against each schema.
        - Scores each schema based on the number of matched tables and columns.
        - Resolves column wildcards (e.g., "orders.*") to match all columns in the specified table.
        - Returns the schema with the highest score, or a list of tied schemas if multiple schemas have the same score.

        Behavior:
        - Wildcard Columns (e.g., "orders.*"): If "IGNORE_COLUMN_WILDCARDS" is False, expands wildcards into individual columns from the schema's table definitions.
        - Single Match: Returns the schema name as a string.
        - Multiple Matches: Returns a list of schema names.
        - No Matches: Returns an empty list.

        Args:
            query_scope (QueryScope): Contains tables and columns specified in the query.
            schemas (List[SchemaTablesResponse]): List of schemas with table and column details.
            tenant_settings (Dict): A dictionary of tenant-specific settings, including "IGNORE_COLUMN_WILDCARDS".

        Returns:
            Union[str, List[str]]: A single schema name if exactly one match, or a list of schema names if multiple schemas are tied.
        """
        query_tables = set(query_scope.entities.tables)
        query_columns = set(query_scope.entities.columns)

        ignore_wildcards = tenant_settings.get("IGNORE_COLUMN_WILDCARDS", True)

        matches = []
        for schema in schemas:
            schema_tables = {table.table_name for table in schema.tables}
            schema_columns = {
                f"{table.table_name}.{column.column_name}"
                for table in schema.tables
                for column in table.columns
            }

            # Expand wildcard columns (e.g., "orders.*") if wildcards are not ignored
            expanded_columns = (
                {col for col in query_columns if not col.endswith(".*")}
                if ignore_wildcards else
                {
                    col for col in query_columns if not col.endswith(".*")
                }.union(
                    {
                        f"{table}.{col}"
                        for column in query_columns if column.endswith(".*")
                        for table in {column.split(".*")[0]}
                        if table in schema_tables
                        for col in {column.column_name for column in schema.tables if table == schema.table_name}
                    }
                )
            )

            # Calculate matches for tables and columns
            table_matches = query_tables & schema_tables
            column_matches = expanded_columns & schema_columns

            # Calculate score: 2 points per table match, 1 point per column match
            score = len(table_matches) * 2 + len(column_matches)

            if score > 0:
                matches.append({"schema_name": schema.schema_name, "score": score})

        if not matches:
            return []

        # Sort matches by score in descending order
        matches.sort(key=lambda x: x["score"], reverse=True)

        if len(matches) == 1:
            # Return the single schema name if there's only one match
            return matches[0]["schema_name"]

        max_score = matches[0]["score"]
        return [
            match["schema_name"]
            for match in matches if match["score"] == max_score
        ]

