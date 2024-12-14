from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError  
from pymongo.errors import PyMongoError 
from utils.database import mongodb
from config import settings 

from api.routers.tenant_manager import router as tenant_manager_router
from api.routers.schema_manager import router as schema_manager_router
from api.routers.ruleset_manager import router as ruleset_manager_router
from api.routers.sql_generation import router as sql_generation_router
from api.routers.external_authentication_wrapper import router as external_authentication_router
from api.core.exceptions.default_exception_handler import database_exception_handler, http_exception_handler, validation_exception_handler

from api.core.services.schema_manager.schema_manager_service import SchemaManagerService
from api.core.services.ruleset_manager.ruleset_manager_service import RulesetManagerService
from api.core.services.tenant_manager.tenant_settings_service import TenantSettingsService
from api.core.services.authentication.session_manager_service import SessionManagerService

from utils.jwt_utils import authenticate_session, validate_api_key

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

@app.on_event("startup")
async def startup_db_client():
    # Establish MongoDB connection first
    await mongodb.connect()  
    # Initialize indexes
    await SchemaManagerService.create_indexes()
    await RulesetManagerService.create_indexes()
    await TenantSettingsService.create_indexes()
    await SessionManagerService.initialize_ttl_index()

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
app.add_exception_handler(ValidationError, validation_exception_handler)

# Register routers here
app.include_router(tenant_manager_router, prefix="/tenant-manager/api", tags=["Tenant Manager"])
app.include_router(schema_manager_router, prefix="/schema-manager/api", tags=["Schema Manager"])
app.include_router(ruleset_manager_router, prefix="/ruleset-manager/api", tags=["Ruleset Manager"])
app.include_router(external_authentication_router, prefix="/external-auth/api", tags=["External Authentication"])
app.include_router(
    sql_generation_router,
    prefix="/sql-generation/api",
    tags=["SQL Generation"],
    dependencies=[Depends(authenticate_session), Depends(validate_api_key)]
)