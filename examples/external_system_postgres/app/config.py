from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "JWT Authentication External Example"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTION_KEY: str = Field(default=None, env="DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTION_KEY")
    DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTION_IV: str = Field(default=None, env="DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTION_IV")
    DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTED_SECRET: str = Field(default=None, env="DEV_EXAMPLE_SQL_CONTEXT_ENCRYPTED_SECRET")

    def get_database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = "dev.env"

settings = Settings()
