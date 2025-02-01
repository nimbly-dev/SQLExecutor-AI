from typing import List, Dict, Any

from utils.database import mongodb
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from pymongo import ASCENDING
from typing import List

from model.schema.schema import Schema
from model.tenant.tenant import Tenant
from model.requests.schema_manager.add_schema_request import AddSchemaRequest
from model.requests.schema_manager.update_schema_request import UpdateSchemaRequest
from model.responses.schema.schema_tables_response import SchemaTablesResponse, ColumnResponse, TableResponse

class SchemaManagerService:
    
    @staticmethod
    async def create_indexes():
        collection_schema = mongodb.db["schemas"]
        collection_schema.create_index([("tenant_id", ASCENDING), ("schema_name", ASCENDING)], unique=True)

    @staticmethod
    async def add_schema(tenant_id: str, schema_request: AddSchemaRequest):
        collection_tenant = mongodb.db["tenants"]
        tenant_dict = await collection_tenant.find_one({"tenant_id": tenant_id})

        if not tenant_dict:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )

        tenant = Tenant(**tenant_dict)
        schema_data = Schema(
            tenant_id=tenant.tenant_id,
            schema_name=schema_request.schema_name,
            description=schema_request.description,
            tables=schema_request.tables,
            filter_rules=schema_request.filter_rules,
            exclude_description_on_generate_sql=schema_request.exclude_description_on_generate_sql,
            synonyms=schema_request.synonyms,
            context_type=schema_request.context_type,
            context_setting=schema_request.context_setting,
            schema_chat_interface_integration=schema_request.schema_chat_interface_integration
        )

        collection_schema = mongodb.db["schemas"]
        
        try:
            result = await collection_schema.insert_one(schema_data.dict())
            return {"message": "Schema added successfully", "schema_id": str(result.inserted_id)}
        except DuplicateKeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Schema with the name '{schema_request.schema_name}' already exists for this tenant."
            )
            
    @staticmethod
    async def get_schema(tenant_id: str, schema_name: str):
        collection = mongodb.db["schemas"]
        schema = await collection.find_one({"tenant_id": tenant_id, "schema_name": schema_name})
        
        if not schema:
            raise HTTPException(
                status_code=404,
                detail=f"No schema found with name '{schema_name}' for tenant '{tenant_id}'."
            )
        
        return Schema(**schema)

    @staticmethod
    async def get_schemas(tenant_id: str) -> List[Schema]:
        collection = mongodb.db["schemas"]
        schemas_cursor = collection.find({"tenant_id": tenant_id})
        schemas = []

        try:
            async for schema_data in schemas_cursor:
                schemas.append(Schema(**schema_data))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse schema data for tenant '{tenant_id}': {e}"
            )

        if not schemas:
            raise HTTPException(
                status_code=404,
                detail=f"No schemas found for tenant '{tenant_id}'."
            )

        return schemas
    
    @staticmethod
    async def get_schemas_names_and_descriptions(tenant_id: str) -> List[Dict[str, Any]]:
        collection = mongodb.db["schemas"]
        schemas_cursor = collection.find(
            {"tenant_id": tenant_id},
            {"schema_name": 1, "description": 1, "context_type": 1, "context_setting": 1, "_id": 0}  
        )

        schemas = []
        async for schema_data in schemas_cursor:
            context_type = schema_data.get("context_type")
            context_setting = schema_data.get("context_setting", {})

            user_identifier = None
            if context_type == "api" and "api_context" in context_setting:
                user_identifier = context_setting["api_context"].get("user_identifier")
            elif context_type == "sql" and "sql_context" in context_setting:
                user_identifier = context_setting["sql_context"].get("user_identifier")

            schemas.append({
                "schema_name": schema_data["schema_name"],
                "description": schema_data["description"],
                "context_type": context_type,
                "user_identifier": user_identifier
            })

        if not schemas:
            raise HTTPException(
                status_code=404,
                detail=f"No schemas found for tenant '{tenant_id}'."
            )

        return schemas

    @staticmethod
    async def get_schema_tables(tenant_id: str) -> List[SchemaTablesResponse]:
        collection = mongodb.db["schemas"]
        schemas_cursor = collection.find(
            {"tenant_id": tenant_id},
            {"schema_name": 1, "tables": 1}
        )

        schemas = []
        async for schema_data in schemas_cursor:
            tables = []
            for table_name, table_obj in schema_data["tables"].items():
                columns = [
                    ColumnResponse(
                        column_name=col_name,
                        type=col_data.get("type", "UNKNOWN"),
                        description=col_data.get("description"),
                        constraints=col_data.get("constraints", []),
                        is_sensitive_column=col_data.get("is_sensitive_column", False)
                    )
                    for col_name, col_data in table_obj["columns"].items()
                ]
                tables.append(TableResponse(
                    table_name=table_name,
                    columns=columns
                ))

            schemas.append(SchemaTablesResponse(
                schema_name=schema_data["schema_name"],
                tables=tables
            ))

        if not schemas:
            raise HTTPException(
                status_code=404,
                detail=f"No schemas found for tenant '{tenant_id}'."
            )

        return schemas

    @staticmethod
    async def update_schema(tenant_id: str, schema_name: str, update_schema_request: UpdateSchemaRequest):
        update_schema_data = update_schema_request.dict(exclude_unset=True)

        if "tables" in update_schema_data:
            update_schema_data["tables"] = {
                table_name: (table.to_dict() if hasattr(table, "to_dict") else table)
                for table_name, table in update_schema_data["tables"].items()
            }

        update_schema_data.pop("schema_name", None)

        collection = mongodb.db["schemas"]
        schema = await collection.find_one({"tenant_id": tenant_id, "schema_name": schema_name})
        if not schema:
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{schema_name}' not found for tenant '{tenant_id}'."
            )

        result = await collection.update_one(
            {"tenant_id": tenant_id, "schema_name": schema_name},
            {"$set": update_schema_data}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{schema_name}' not found for tenant '{tenant_id}' or no changes were made."
            )

        return {"message": f"Schema '{schema_name}' updated successfully for tenant '{tenant_id}'."}

    @staticmethod
    async def delete_schema(tenant_id: str, schema_name: str):
        collection = mongodb.db["schemas"]
        result = await collection.delete_one({"tenant_id": tenant_id, "schema_name": schema_name})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Schema not found"
            )
        
        return {"message": "Schema deleted successfully"}
