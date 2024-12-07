from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError 
from utils.database import mongodb
from config import settings 

from api.routers.tenant_manager import router as tenant_manager_router
from api.core.exceptions.default_exception_handler import database_exception_handler, http_exception_handler, validation_exception_handler

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

@app.on_event("startup")
async def startup_db_client():
    await mongodb.connect()  

@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.disconnect()  

@app.get("/")
async def health_check():
    try:
        await mongodb.client.admin.command('ping')
        return {
            "backend_status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode",
            "mongodb_status": "SQLExecutor is connected to MongoDB"
        }
    except Exception as e:
        print(f"Healthcheck failed: {e}")
        return {
            "backend_status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode",
            "mongodb_status": "Failed to connect to MongoDB"
        }

# Register Exceptions here
app.add_exception_handler(PyMongoError, database_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Register routers here
app.include_router(tenant_manager_router, prefix="/tenant-manager/api", tags=["Tenant Manager"])
