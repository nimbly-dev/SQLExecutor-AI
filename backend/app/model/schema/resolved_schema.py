from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class ResolvedJoin(BaseModel):
    description: Optional[str] = None
    table: str  
    on: str  
    type: str 

class ResolvedColumn(BaseModel):
    type: str
    description: Optional[str] = Field(default=None, exclude_unset=True)
    synonyms: Optional[List[str]] = Field(default=None, exclude_none=True)

class ResolvedTable(BaseModel):
    description: Optional[str] = Field(default=None, exclude_unset=True)
    synonyms: Optional[List[str]] = Field(default_factory=list, exclude_unset=True)
    columns: Dict[str, ResolvedColumn]
    relationships: Optional[Dict[str, ResolvedJoin]] = Field(default_factory=dict, exclude_unset=True)

class ResolvedSchema(BaseModel):
    tables: Dict[str, ResolvedTable]
    description: Optional[str] = Field(default=None, exclude_unset=True)
