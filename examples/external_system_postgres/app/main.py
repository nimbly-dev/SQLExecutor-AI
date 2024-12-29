import json
from fastapi import FastAPI, HTTPException, Depends, Header
from config import settings 

from routes.auth_route import router as auth_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

@app.get("/")
def health_check():
    return {"status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode"}

app.include_router(auth_router, prefix="", tags=["Authentication"])