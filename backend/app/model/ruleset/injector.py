from pydantic import BaseModel, Field
from typing import Dict, Optional

class InjectorCondition(BaseModel):
    condition: str = Field(..., description="Condition to evaluate against session data.")

class InjectorTableRule(BaseModel):
    filters: str = Field(..., description="SQL filter clause, e.g., 'user_id = ${jwt.user_id}'.")

class Injector(BaseModel):
    name: str = Field(..., description="Unique name for the injector.")
    enabled: bool = Field(True, description="Enable or disable the injector.")
    condition: InjectorCondition = Field(..., description="Condition to activate the injector.")
    tables: Dict[str, InjectorTableRule] = Field(
        ..., description="Mapping of tables to filter rules."
    )
