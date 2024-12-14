import json
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from config import settings 
from model.token import Token
from model.loginrequest import LoginRequest

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

active_sessions = set()

def load_users():
    try:
        with open(settings.USER_DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

users_db = load_users()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@app.get("/")
def health_check():
    return {"status": f"{settings.APP_NAME} is running in {settings.APP_ENV} mode"}

@app.post("/login", response_model=Token)
def login(request: LoginRequest):
    user = users_db.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"tenant_id":"TENANT_TST2","sub": request.username, "roles": user["roles"]})
    active_sessions.add(request.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in active_sessions:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        active_sessions.remove(username)
        return {"message": "Logout successful"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
