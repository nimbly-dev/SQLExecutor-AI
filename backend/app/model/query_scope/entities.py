from pydantic import BaseModel
from typing import List, Optional

class Entities(BaseModel):
    tables: List[str]
    columns: List[str]
    sensitive_columns: List[str] = []
