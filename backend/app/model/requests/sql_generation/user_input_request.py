from pydantic import BaseModel, Field, root_validator

class UserInputRequest(BaseModel):
    input: str