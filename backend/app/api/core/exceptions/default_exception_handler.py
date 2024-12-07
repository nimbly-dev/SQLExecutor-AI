from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, HTTPException
from pymongo.errors import PyMongoError
from pydantic import ValidationError  

async def database_exception_handler(request, exc: PyMongoError):
    return JSONResponse(
        content={"detail": "Database error occurred. Please try again later."},
    )

async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, ValidationError):
        error_detail = []
        for error in exc.errors():
            error_detail.append({
                "msg": error["msg"],  
                "type": error["type"],  
            })
        return JSONResponse(
            status_code=400,
            content={"detail": error_detail},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": [{"msg": "Internal Server Error"}]},
    )