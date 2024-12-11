from pydantic import BaseModel
from typing import List

class Entities(BaseModel):
    tables: List[str]
    columns: List[str]
