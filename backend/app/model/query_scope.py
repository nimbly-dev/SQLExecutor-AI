from pydantic import BaseModel

from model.entities import Entities

class QueryScope(BaseModel):
    intent: str
    entities: Entities
