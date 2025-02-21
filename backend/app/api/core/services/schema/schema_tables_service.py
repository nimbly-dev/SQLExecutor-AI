from utils.database import mongodb
from typing import List
from fastapi import HTTPException

from model.responses.schema.schema_tables_response import SimpleTableColumnsNameResponse, SimpleColumnResponse
from api.core.services.schema.schema_manager_service import SchemaManagerService

class SchemaTablesService:
    
    @staticmethod
    async def get_tables_of_schema(tenant_id: str, schema_name: str) -> List[SimpleTableColumnsNameResponse]:
        schema = await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=schema_name)
        if not schema:
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{schema_name}' not found for tenant '{tenant_id}'"
            )
        
        tables_list = []
        for table_name, table in schema.tables.items():
            columns = [
                SimpleColumnResponse(
                    column_name=col_name,
                    is_sensitive_column=col_info.is_sensitive_column
                )
                for col_name, col_info in table.columns.items()
            ]
            
            tables_list.append(
                SimpleTableColumnsNameResponse(
                    table_name=table_name,
                    columns=columns
                )
            )
        
        return tables_list