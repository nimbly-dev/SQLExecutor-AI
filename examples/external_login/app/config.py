from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "JWT Authentication External Example"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    USER_DB_FILE: str = "./resources/sample_users.json"

    class Config:
        env_file = "dev.env"

settings = Settings()
