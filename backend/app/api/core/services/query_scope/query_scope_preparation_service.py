import logging
from typing import List
from fastapi import HTTPException


from model.query_scope import QueryScope
from model.responses.schema.schema_tables_response import SchemaTablesResponse
from api.core.services.schema.schema_manager_service import SchemaManagerService
from utils.query_scope.validate_query_scope_utils import ValidateQueryScopeUtils


logger = logging.getLogger(__name__)


class QueryScopePreparationService:
    """
    Service to fetch schemas, apply soft preprocessing, and validate tables
    before proceeding with QueryScope resolution.
    """

    @staticmethod
    def _soft_preprocess_tables(schemas: List[SchemaTablesResponse], query_scope: QueryScope) -> None:
        """
        Soft pre-process table names and associated column names in the query scope
        by correcting minor errors (e.g., missing or extra 's').
        Modifies the query_scope in place.
        """
        valid_tables = set()
        for schema in schemas:
            if isinstance(schema, SchemaTablesResponse):
                valid_tables.update(table.table_name for table in schema.tables)
            else:
                raise AttributeError(
                    f"Expected SchemaTablesResponse object, but got {type(schema)}"
                )

        corrected_tables = []
        table_name_mapping = {}

        for table in query_scope.entities.tables:
            if table in valid_tables:
                corrected_tables.append(table)
                table_name_mapping[table] = table
            elif table + "s" in valid_tables:  # missing 's'
                corrected_name = table + "s"
                corrected_tables.append(corrected_name)
                table_name_mapping[table] = corrected_name
                logger.debug(f"Soft fix applied: '{table}' -> '{corrected_name}'")
            elif table.endswith("s") and (table[:-1] in valid_tables):  # extra 's'
                corrected_name = table[:-1]
                corrected_tables.append(corrected_name)
                table_name_mapping[table] = corrected_name
                logger.debug(f"Soft fix applied: '{table}' -> '{corrected_name}'")
            else:
                corrected_tables.append(table)
                table_name_mapping[table] = table
                logger.debug(f"No soft fix applied for: '{table}'")

        corrected_columns = []
        for column in query_scope.entities.columns:
            if "." in column:
                table_name, column_name = column.split(".", 1)
                corrected_table_name = table_name_mapping.get(table_name, table_name)
                corrected_columns.append(f"{corrected_table_name}.{column_name}")
            else:
                corrected_columns.append(column)

        query_scope.entities.tables = corrected_tables
        query_scope.entities.columns = corrected_columns

    @staticmethod
    async def prepare_query_scope(tenant_id: str, query_scope: QueryScope) -> List[SchemaTablesResponse]:
        """
        Fetch schemas for a tenant, soft-preprocess table and column names,
        then validate the existence of the tables in the schemas.
        Returns a list of SchemaTablesResponse objects.
        """
        schemas = await SchemaManagerService.get_schema_tables(tenant_id=tenant_id)
        QueryScopePreparationService._soft_preprocess_tables(schemas, query_scope)

        tables_exist = ValidateQueryScopeUtils.validate_tables_exist_in_schemas(
            schemas, query_scope
        )
        if not tables_exist:
            raise HTTPException(
                status_code=400,
                detail="One or more tables in the user request do not exist in the schemas."
            )

        return schemas