from fastapi import APIRouter

from api.core.services.schema_manager.schema_manager_service import SchemaManagerService
from model.requests.schema_manager.add_schema_request import AddSchemaRequest
from model.requests.schema_manager.update_schema_request import UpdateSchemaRequest

router = APIRouter()

@router.post("/schemas/{tenant_id}")
async def add_schema(tenant_id: str, schema_request: AddSchemaRequest):
    return await SchemaManagerService.add_schema(tenant_id=tenant_id, schema_request=schema_request)


@router.get("/schemas/{tenant_id}/{schema_name}")
async def get_schema(tenant_id: str, schema_name: str):
    return await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=schema_name)

@router.put("/schemas/{tenant_id}/{schema_name}")
async def get_schema(tenant_id: str, schema_name: str, schema_request: UpdateSchemaRequest):
    return await SchemaManagerService.update_schema(tenant_id=tenant_id, schema_name=schema_name, update_schema_request=schema_request)

@router.delete("/schemas/{tenant_id}/{schema_name}")
async def delete_schema(tenant_id: str, schema_name: str):
    return await SchemaManagerService.delete_schema(tenant_id=tenant_id, schema_name=schema_name)