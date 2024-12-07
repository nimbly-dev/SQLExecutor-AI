from utils.database import mongodb
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from pymongo import ASCENDING

from model.schema import Schema
from model.tenant import Tenant
from model.requests.schema_manager.add_schema_request import AddSchemaRequest
from model.requests.schema_manager.update_schema_request import UpdateSchemaRequest

class SchemaManagerService:
    
    @staticmethod
    async def create_indexes():
        # Enforce uniqueness on the schema_name field within the same tenant
        collection_schema = mongodb.db["schemas"]
        collection_schema.create_index([("tenant_id", ASCENDING), ("schema_name", ASCENDING)], unique=True)
    
    @staticmethod
    async def add_schema(tenant_id: str, schema_request: AddSchemaRequest):
        collection_tenant = mongodb.db["tenants"]
        tenant_dict = await collection_tenant.find_one({"tenant_id": tenant_id})
        
        # If tenant is not found, raise an HTTPException
        if not tenant_dict:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )

        # Convert the tenant data to the Tenant model
        tenant = Tenant(**tenant_dict)
        
        # Create Schema Data from the request
        schema_data = Schema(
            tenant_id=tenant.tenant_id,
            schema_name=schema_request.schema_name,
            description=schema_request.description,
            tables=schema_request.tables,
            filter_rules=schema_request.filter_rules
        )
        
        # Insert schema into the schemas collection
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
    async def update_schema(tenant_id: str, schema_name: str, update_schema_request: UpdateSchemaRequest):
        update_schema_data = update_schema_request.dict(exclude_unset=True)

        if "tables" in update_schema_data:
            update_schema_data["tables"] = {
                table_name: (table.to_dict() if hasattr(table, "to_dict") else table)
                for table_name, table in update_schema_data["tables"].items()
            }

        update_schema_data.pop("schema_name", None)

        collection = mongodb.db["schemas"]
        # Check if the schema exists
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

        # Check if the update matched any documents
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
    