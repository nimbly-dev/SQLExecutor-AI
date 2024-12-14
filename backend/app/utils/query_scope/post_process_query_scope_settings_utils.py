from model.tenant import Tenant
from model.setting import Setting
from model.schema import Schema
from model.query_scope import QueryScope
from model.entities import Entities

class PostProcessQueryScopeSettingsUtils:
    
    @staticmethod
    def remove_missing_columns_from_query_scope(schema: Schema, query_scope: QueryScope) -> QueryScope:
        """
        Key: (IGNORE_MISSING_COLUMN_ON_QUERY_SCOPE) 
        Removes columns from query_scope that do not exist in the schema.

        Args:
            schema (Schema): The schema object containing table and column information.
            query_scope (QueryScope): The query scope object defining the intent and entities.

        Returns:
            QueryScope: The updated query scope with missing columns removed.
        """
        tables = query_scope.entities.tables
        columns = query_scope.entities.columns

        schema_table_map = {table_name: table for table_name, table in schema.tables.items()}
        for table_name, table in schema.tables.items():
            for synonym in table.synonyms or []:
                schema_table_map[synonym] = table

        valid_columns = []

        for column in columns:
            if column == "*":  
                valid_columns.append(column)
                continue

            if "." in column:
                table_name, column_name = column.split(".", 1)
                if table_name in schema_table_map:
                    table = schema_table_map[table_name]
                    if column_name in table.columns:
                        valid_columns.append(column)

        updated_entities = Entities(
            tables=tables,
            columns=valid_columns
        )

        return query_scope.copy(update={"entities": updated_entities})