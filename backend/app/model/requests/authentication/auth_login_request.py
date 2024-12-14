from pydantic import BaseModel, Field, root_validator

class AuthLoginRequest(BaseModel):
    auth_tenant_id: str =  Field(..., description="Tenant ID where the requests comes from")
    auth_field: str = Field(..., description="The dynamic authentication field, e.g., username or email.")
    auth_passkey_field: str = Field(..., description="The dynamic passkey field, e.g., password or OTP.")

    @root_validator(pre=True)
    def validate_required_fields(cls, values):
        if not values.get("auth_tenant_id"):
            raise ValueError("auth_tenant_id is required and cannot be empty.")
        
        if not values.get("auth_field"):
            raise ValueError("auth_field is required and cannot be empty.")
        
        if not values.get("auth_passkey_field"):
            raise ValueError("auth_passkey_field is required and cannot be empty.")
        
        return values
