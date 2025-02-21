from pydantic import BaseModel, Field
from typing import Dict

class InjectorTableRule(BaseModel):
    filters: str = Field(..., description="SQL filter clause, e.g., 'user_id = ${jwt.user_id}'.")

class Injector(BaseModel):
    enabled: bool = Field(True, description="Enable or disable the injector.")
    condition: str = Field(..., description="Condition to evaluate against session data.")
    tables: Dict[str, InjectorTableRule] = Field(
        ..., description="Mapping of tables to filter rules."
    )
