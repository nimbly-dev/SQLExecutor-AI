from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.core.services.schema.schema_manager_service import SchemaManagerService
from api.core.services.schema.schema_tables_service import SchemaTablesService;

from model.requests.schema_manager.add_schema_request import AddSchemaRequest
from model.responses.schema.schema_tables_response import SchemaTablesResponse
from model.requests.schema_manager.update_schema_request import UpdateSchemaRequest
from model.authentication.admin_session_data import AdminSessionData

from utils.auth_utils import authenticate_admin_session

router = APIRouter()

from fastapi import APIRouter, Query, HTTPException, Depends

@router.get("/{tenant_id}/schemas")
async def get_schemas(
    tenant_id: str,
    summary: bool = Query(False),
    summary_paginated: bool = Query(False),
    name: Optional[str] = Query(None),
    filter_name: Optional[str] = Query(None),
    context_type: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(10),
    admin_session_data: AdminSessionData = Depends(authenticate_admin_session)
):
    if admin_session_data.role not in ["Schema Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )

    if summary and summary_paginated:
        raise HTTPException(
            status_code=400,
            detail="Cannot use both 'summary' and 'summary_paginated' query parameters simultaneously."
        )

    if summary:
        return await SchemaManagerService.get_schemas_names_and_descriptions(tenant_id=tenant_id)

    if summary_paginated:
        # Use the dedicated filter parameter for paginated queries.
        # If 'filter_name' is not provided, fallback to 'name' (but avoid ambiguity with single schema retrieval).
        effective_filter = filter_name if filter_name is not None else name
        return await SchemaManagerService.get_schemas_names_and_descriptions_paginated(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            filter_name=effective_filter,
            context_type=context_type
        )

    if name:
        schema = await SchemaManagerService.get_schema(tenant_id=tenant_id, schema_name=name)
        if not schema:
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{name}' not found for tenant '{tenant_id}'."
            )
        return schema

    return await SchemaManagerService.get_all_schemas(tenant_id=tenant_id)


@router.post("/{tenant_id}/schemas")
async def add_schema(tenant_id: str, schema_request: AddSchemaRequest, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Schema Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await SchemaManagerService.add_schema(tenant_id=tenant_id, schema_request=schema_request)

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

# Schema Tables API Endpoints
@router.get("/{tenant_id}/schemas/{schema_name}/tables")
async def get_tables(tenant_id: str, schema_name: str, admin_session_data: AdminSessionData = Depends(authenticate_admin_session)):
    if admin_session_data.role not in ["Schema Admin", "Tenant Admin"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action"
        )
    return await SchemaTablesService.get_tables_of_schema(tenant_id=tenant_id, schema_name=schema_name)