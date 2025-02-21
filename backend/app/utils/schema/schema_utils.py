from utils.database import mongodb
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService

async def schema_exists(tenant_id: str, schema_name: str) -> bool:
    tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    collection = mongodb.db["schemas"]
    
    schema = await collection.find_one(
        {"tenant_id": tenant.tenant_id, "schema_name": schema_name},
        {"_id": 1}
    )
    
    return schema is not None
