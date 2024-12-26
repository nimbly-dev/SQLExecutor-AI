from pydantic import BaseModel, Field
from uuid import UUID
import bcrypt

class AdminUser(BaseModel):
    user_id: str = Field(..., description="The user identifier.")
    password: str = Field(..., description="The hashed user password.")
    role: str = Field(..., description="Role of the Admin")

    def verify_password(self, plain_password: str) -> bool:
        """Verify if the provided plain password matches the stored hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))