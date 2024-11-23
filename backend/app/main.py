from fastapi import FastAPI
from config import settings  # Importing directly, as config.py is in the same directory

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

@app.get("/")
def health_check():
    return {"status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode"}
