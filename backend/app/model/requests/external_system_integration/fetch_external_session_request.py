from pydantic import BaseModel

class FetchExternalSession(BaseModel):
    external_session_id: str