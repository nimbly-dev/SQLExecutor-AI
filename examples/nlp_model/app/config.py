from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "External OpenAI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    OPENAI_API_KEY: str 

    class Config:
        env_file = ".env"

settings = Settings()
