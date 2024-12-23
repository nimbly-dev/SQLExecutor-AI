from pydantic import BaseModel, Field, root_validator
from typing import List, Dict, Optional, Any

class Criteria(BaseModel):
    matching_criteria: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs defining the matching criteria for the policy, supports nested structures."
    )
    condition: Optional[str] = Field(
        None,
        description="Optional condition string for advanced logic."
    )