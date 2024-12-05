from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from config import settings  # Importing directly, as config.py is in the same directory

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

client = MongoClient(settings.mongodb_uri)

@app.get("/")
def health_check():
    try:
        client.admin.command('ping')
        return {
            "backend_status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode",
            "mongodb_status": f"SQLExecutor is connected to MongoDB"
        }
    except Exception as e:
        print(e)
        return{
            "SQLExecutor Application Healthcheck failed"
        }
