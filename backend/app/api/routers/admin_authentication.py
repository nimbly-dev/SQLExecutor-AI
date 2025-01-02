from fastapi import APIRouter, HTTPException, Header
from model.requests.authentication.auth_admin_login_request import AuthLoginRequest

from api.core.services.authentication.admin_authentication_service import AdminAuthenticationService

router = APIRouter()

@router.post("/login")
async def login_admin(auth_request: AuthLoginRequest):
    return await AdminAuthenticationService.login_admin(auth_request=auth_request)

@router.post("/logout")
async def logout_external_user(authorization: str = Header(...)):
    """
    Logout admin using Authorization header.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    return await AdminAuthenticationService.logout_admin_from_token(token)
