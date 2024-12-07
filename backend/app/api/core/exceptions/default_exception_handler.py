from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, HTTPException
from pymongo.errors import PyMongoError  

async def database_exception_handler(request, exc: PyMongoError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred. Please try again later."},
    )

async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Modify the error response to omit the "loc" field
    error_detail = []
    for error in exc.errors():
        error_detail.append({
            "msg": error["msg"],  # Keep the message
            "type": error["type"],  # Keep the type
        })

    return JSONResponse(
        status_code=422,
        content={"detail": error_detail},
    )