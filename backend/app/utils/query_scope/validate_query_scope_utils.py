from typing import List, Tuple
from model.schema.schema import Schema
from model.query_scope.query_scope import QueryScope
from model.responses.schema.schema_tables_response import SchemaTablesResponse

class ValidateQueryScopeUtils:
    
    @staticmethod
    def validate_tables_exist_in_schemas(schemas: List[SchemaTablesResponse], query_scope: QueryScope) -> Tuple[bool, List[str]]: 
        """
        Validates if all tables in the query_scope exist in the provided schema data.

        Args:
            schemas (List[SchemaTablesResponse]): A list of simplified schema responses.
            query_scope (QueryScope): The query scope object defining the intent and entities.

        Returns:
            bool: True if all tables exist in at least one schema, False otherwise.
        """
        tables_to_validate = set(query_scope.entities.tables)

        # Create a set of all valid table names
        valid_tables = {table.table_name for schema in schemas for table in schema.tables}

        unmatched = list(tables_to_validate - valid_tables)
        return (len(unmatched) == 0, unmatched)