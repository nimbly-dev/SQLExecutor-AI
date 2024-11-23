from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SQLExecutor"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

# Create a single instance of the Settings class
settings = Settings()
