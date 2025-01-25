from pydantic import BaseModel

class CreateExternalSessionRequest(BaseModel):
    context_user_identifier_value: str