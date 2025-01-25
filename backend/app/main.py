from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError  
from pymongo.errors import PyMongoError 
from utils.database import mongodb
from config import settings 
from fastapi.middleware.cors import CORSMiddleware

from api.routers.tenant_manager import router as tenant_manager_router
from api.routers.schema_manager import router as schema_manager_router
from api.routers.ruleset_manager import router as ruleset_manager_router
from api.routers.sql_generation import router as sql_generation_router
from api.routers.admin_authentication import router as admin_authentication_router
from api.routers.sql_context import router as sql_context_router
from api.routers.api_context import router as api_context_router
from api.routers.chat_interface import router as chat_interface_router
from api.core.exceptions.default_exception_handler import database_exception_handler, http_exception_handler, validation_exception_handler

from api.core.services.schema.schema_manager_service import SchemaManagerService
from api.core.services.ruleset.ruleset_manager_service import RulesetManagerService
from api.core.services.tenant_manager.tenant_settings_service import TenantSettingsService
from api.core.services.tenant_manager.admin_user_manager_service import AdminUserService
from api.core.services.external_system.external_session_manager_service import SessionManagerService
from api.core.services.authentication.admin_authentication_service import AdminAuthenticationService
from api.core.services.authentication.admin_session_manager_service import AdminSessionManagerService

from utils.auth_utils import authenticate_session, validate_api_key, authenticate_admin_session

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
    # await TenantSettingsService.create_indexes()
    await SessionManagerService.initialize_ttl_index()
    await AdminSessionManagerService.initialize_ttl_index()

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

# SANDBOX TENANT ADMIN ROUTES
app.include_router(tenant_manager_router, prefix="/v1/tenants", tags=["Tenant Manager"])
app.include_router(schema_manager_router, prefix="/v1/schema-manager", tags=["Schema Manager"])
app.include_router(ruleset_manager_router, prefix="/v1/ruleset-manager", tags=["Ruleset Manager"])
app.include_router(admin_authentication_router, prefix="/v1/admin-auth", tags=["Admin Authentication"])
app.include_router(
    chat_interface_router,
    prefix="/v1/chat-interface",
    tags=["Chat Interface"],
    dependencies=[Depends(authenticate_admin_session)]
)

# END USERS ROUTES
app.include_router(
    sql_generation_router,
    prefix="/v1/sql-generation",
    tags=["SQL Generation"],
    dependencies=[Depends(authenticate_session), Depends(validate_api_key)]
)
app.include_router(
    sql_context_router,
    prefix="/v1/sql-context",
    tags=["SQL Context"],
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    api_context_router,
    prefix="/v1/api-context",
    tags=["API Context"],
    dependencies=[Depends(validate_api_key)]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://localhost:3000"] in production for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)