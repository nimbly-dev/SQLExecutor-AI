from pydantic import BaseModel

class InvalidateExternalSession(BaseModel):
    external_session_id: str