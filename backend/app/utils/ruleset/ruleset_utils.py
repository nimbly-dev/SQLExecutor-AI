from utils.database import mongodb
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService

def extract_ruleset_name(ruleset_placeholder: str) -> str:
    """
    Extract and clean the ruleset name from a placeholder string.

    Args:
        ruleset_placeholder (str): Placeholder string with ${}.

    Returns:
        str: The cleaned ruleset name without ${}.
    """
    if ruleset_placeholder.startswith("${") and ruleset_placeholder.endswith("}"):
        return ruleset_placeholder[2:-1]
    raise ValueError(f"Invalid ruleset format: {ruleset_placeholder}")

def resolve_field(data, path):
    """
    Resolve a nested field in a dictionary given a dot-separated path.
    """
    keys = path.split(".")

    for key in keys:
        if key in data:
            data = data[key]
        elif "custom_fields" in data and key in data["custom_fields"]:
            data = data["custom_fields"][key]
        else:
            return None
    return data

async def ruleset_exists(tenant_id: str, ruleset_name: str) -> bool:
    tenant = await TenantManagerService.get_tenant(tenant_id=tenant_id)
    collection = mongodb.db["rulesets"]
    
    ruleset = await collection.find_one(
        {"tenant_id": tenant.tenant_id, "ruleset_name": ruleset_name},
        {"_id": 1}
    )
    
    return ruleset is not None
