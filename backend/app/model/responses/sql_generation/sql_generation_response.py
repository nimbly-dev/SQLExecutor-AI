from pydantic import BaseModel
from typing import Any

from model.query_scope.query_scope import QueryScope

class SqlGenerationResponse(BaseModel):
    query_scope: QueryScope
    user_input: str
    sql_query: str
    sql_response: Any
    injected_str: str = None