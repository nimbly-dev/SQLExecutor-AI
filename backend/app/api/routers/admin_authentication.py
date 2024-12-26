from fastapi import APIRouter, HTTPException
from model.requests.authentication.auth_admin_login_request import AuthLoginRequest

from api.core.services.authentication.admin_authentication_service import AdminAuthenticationService

router = APIRouter()

@router.post("/login")
async def login_admin(auth_request: AuthLoginRequest):
    return await AdminAuthenticationService.login_admin(auth_request=auth_request)
    