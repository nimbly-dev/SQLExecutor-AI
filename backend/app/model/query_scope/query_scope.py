from pydantic import BaseModel

from model.query_scope.entities import Entities

class QueryScope(BaseModel):
    intent: str
    entities: Entities
