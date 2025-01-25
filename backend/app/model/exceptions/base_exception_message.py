from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class BaseExceptionMessage(BaseModel):
    reason: Optional[str] = None 
    message: str
    stacktrace: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"