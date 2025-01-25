from typing import Dict, Optional
from pydantic import BaseModel, Field, root_validator


class ContextUserRow(BaseModel):
    context_identifier: str = Field(..., description="The user identifier.")
    custom_fields: Dict[str, str] = Field(
        default_factory=dict, 
        description="Key-value pairs of custom fields to be printed alongside the Select Context User Impersonation Modal."
    )
