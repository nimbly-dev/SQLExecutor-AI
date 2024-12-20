from utils.database import mongodb
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from pymongo import ASCENDING
from typing import List, Dict, Union

from model.schema import Schema
from model.tenant import Tenant
from model.query_scope import QueryScope
from model.responses.schema.schema_tables_response import SchemaTablesResponse

from utils.query_scope.query_scope_utils import expand_columns
class SchemaDiscoveryService:
                
    @staticmethod
    def get_best_matching_schemas(query_scope: QueryScope, schemas: List[SchemaTablesResponse], tenant_settings: Dict) -> Union[str, List[str]]:
        """
        Matches the provided query scope to the most relevant schemas for a tenant.

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
            schema_columns_dict = {
                table.table_name: [column.column_name for column in table.columns]
                for table in schema.tables
            }

            # Expand columns using the utility function
            expanded_columns = expand_columns(
                query_columns=query_columns,
                schema_tables=schema_tables,
                schema_columns=schema_columns_dict
            ) if not ignore_wildcards else query_columns

            # Flatten schema columns for matching
            flattened_schema_columns = {
                f"{table}.{column}"
                for table, columns in schema_columns_dict.items()
                for column in columns
            }

            # Calculate matches for tables and columns
            table_matches = query_tables & schema_tables
            column_matches = expanded_columns & flattened_schema_columns

            # Calculate score: 2 points per table match, 1 point per column match
            score = len(table_matches) * 2 + len(column_matches)

            if score > 0:
                matches.append({"schema_name": schema.schema_name, "score": score})

        if not matches:
            return []

        # Sort matches by score in descending order
        matches.sort(key=lambda x: x["score"], reverse=True)

        if len(matches) == 1:
            return matches[0]["schema_name"]

        max_score = matches[0]["score"]
        return [match["schema_name"] for match in matches if match["score"] == max_score]