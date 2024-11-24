from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SQLExecutor"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    MODEL: str = "tiiuae/falcon-7b-instruct"

# Create a single instance of the Settings class
settings = Settings()
