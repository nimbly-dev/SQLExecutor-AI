from fastapi import APIRouter, Depends, HTTPException, Query

from api.core.services.schema.schema_manager_service import SchemaManagerService
from model.requests.schema_manager.add_schema_request import AddSchemaRequest
from model.requests.schema_manager.update_schema_request import UpdateSchemaRequest
from model.authentication.admin_session_data import AdminSessionData

from utils.auth_utils import authenticate_admin_session

router = APIRouter()

@router.post("/{tenant_id}/schemas/")
async def add_schema(tenant_id: str, schema_request: AddSchemaRequest, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Schema Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await SchemaManagerService.add_schema(tenant_id=tenant_id, schema_request=schema_request)

@router.get("/{tenant_id}/schemas")
async def get_schemas(
    tenant_id: str,
    summary: bool = Query(False),  
    name: str | None = Query(None), 
    admin_session_data: AdminSessionData = Depends(authenticate_admin_session)
):
    if admin_session_data.role not in ["Schema Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )

    if summary:
        return await SchemaManagerService.get_schemas_names_and_descriptions(tenant_id=tenant_id)

    if name:
        schema = await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=name)
        if not schema:
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{name}' not found for tenant '{tenant_id}'."
            )
        return schema

    return await SchemaManagerService.get_all_schemas(tenant_id=tenant_id)

@router.put("/{tenant_id}/schemas/{schema_name}")
async def update_schema(tenant_id: str, schema_name: str, schema_request: UpdateSchemaRequest,  admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Schema Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await SchemaManagerService.update_schema(tenant_id=tenant_id, schema_name=schema_name, update_schema_request=schema_request)

@router.delete("/{tenant_id}/schemas/{schema_name}")
async def delete_schema(tenant_id: str, schema_name: str,  admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Schema Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await SchemaManagerService.delete_schema(tenant_id=tenant_id, schema_name=schema_name)