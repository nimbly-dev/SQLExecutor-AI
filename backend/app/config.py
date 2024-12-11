from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SQLExecutor"
    APP_VERSION: str = "0.3.2"
    APP_ENV: str = "development"
    DEFAULT_APP_LLM_MODEL = "gpt-4o-mini"

    DEV_SERVICE_ACCOUNT_PASSWORD: str
    DEV_USERNAME: str
    CLUSTER_DB_URL: str
    MONGO_DB_NAME: str    
    OPENAI_API_KEY: str

    @property
    def mongodb_uri(self) -> str:
        return f"mongodb+srv://{self.DEV_USERNAME}:{self.DEV_SERVICE_ACCOUNT_PASSWORD}@{self.CLUSTER_DB_URL}"

    class Config:
        env_file = ".env"


settings = Settings()
