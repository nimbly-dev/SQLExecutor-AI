from fastapi import APIRouter, HTTPException, Depends, Header
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from config import settings
from db.database import get_db
from db.orm_models import User, Role, Admin

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

active_sessions = set()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Check user role
    role = db.query(Role).filter(Role.user_id == user.user_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role not assigned to user")

    # Check if user is an admin
    admin = db.query(Admin).filter(Admin.user_id == user.user_id).first()
    is_admin = bool(admin)

    # Generate token
    access_token = create_access_token(data={
        "sub": request.username,
        "role": role.role,
        "is_admin": is_admin,
        "is_active": user.is_active,
        "user_id": user.user_id
    })
    active_sessions.add(request.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username not in active_sessions:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        active_sessions.remove(username)
        return {"message": "Logout successful"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
