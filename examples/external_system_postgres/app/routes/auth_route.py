from fastapi import APIRouter, HTTPException, Depends, Header,  Query
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from config import settings
from db.database import get_db
from db.orm_models import User, Role, Admin
from model.get_users_response import GetUsersResponse
from sqlalchemy import text
import hmac
import hashlib
import time

SHARED_SECRET_KEY = "demo_secret_key_123456"

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

active_sessions = set()

def generate_hmac_signature(shared_secret: str, user_identifier: str) -> dict:
    """Generate HMAC signature for the request"""
    timestamp = str(int(time.time())) 
    message = f"{user_identifier}:{timestamp}"  # Format: user_identifier:timestamp
    signature = hmac.new(shared_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return {"signature": signature, "timestamp": timestamp}

def validate_hmac_signature(shared_secret: str, user_identifier: str, provided_signature: str, timestamp: str):
    """Validate the HMAC signature"""
    # Recreate the message
    message = f"{user_identifier}:{timestamp}"
    expected_signature = hmac.new(shared_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    # Check if signatures match
    if not hmac.compare_digest(expected_signature, provided_signature):
        raise ValueError("Invalid HMAC signature")

    # Check for replay attacks (e.g., timestamp is too old)
    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > 300:  # Allow 5-minute drift
        raise ValueError("Request timestamp expired")

def validate_hmac_signature_for_get_users(shared_secret: str, page: int, limit: int, order_direction: str, timestamp: str, provided_signature: str):
    """Validate the HMAC signature for get-users"""
    message = f"{page}:{limit}:{order_direction}:{timestamp}"
    expected_signature = hmac.new(shared_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, provided_signature):
        raise ValueError("Invalid HMAC signature")

    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > 300:  
        raise ValueError("Request timestamp expired")
    
def validate_hmac_signature_for_context_counts(shared_secret: str, timestamp: str, provided_signature: str):
    """Validate the HMAC signature for get-users-context-counts."""
    message = f"{timestamp}"  # For counts, only timestamp is needed
    expected_signature = hmac.new(shared_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, provided_signature):
        raise ValueError("Invalid HMAC signature")

    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > 300:  # Allow 5-minute drift
        raise ValueError("Request timestamp expired")



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.get("/get-users-context-counts")
async def get_users_context_counts(
    authorization: str = Header(...),
    x_timestamp: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Get the total count of users in the context table.
    """
    print(f"Timestamp Received: {x_timestamp}")
    try:
        # Validate HMAC
        if not authorization.startswith("HMAC "):
            raise ValueError("Invalid Authorization header format")
        provided_signature = authorization.split(" ")[1]
        validate_hmac_signature_for_context_counts(
            SHARED_SECRET_KEY,
            x_timestamp,
            provided_signature
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    try:
        # Query to count total users
        total_users = db.query(User).count()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"total_users": total_users}


@router.get("/get-users", response_model=List[GetUsersResponse])
async def get_users(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    order_by: str = Query("username", description="Field to order by (e.g., username, is_active)"),
    order_direction: str = Query("ASC", regex="^(ASC|DESC)$", description="Ordering direction (ASC or DESC)"),
    authorization: str = Header(...),
    x_timestamp: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Get users with pagination and ordering, returning a list of users with their custom fields.
    """
    print(f"Timestamp Received: {x_timestamp}")
    try:
        if not authorization.startswith("HMAC "):
            raise ValueError("Invalid Authorization header format")
        provided_signature = authorization.split(" ")[1]
        validate_hmac_signature_for_get_users(
            SHARED_SECRET_KEY,
            page,
            limit,
            order_direction,
            x_timestamp,
            provided_signature,
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Validate order_by field
    if order_by not in ["username", "is_active", "email"]:  # Adjust based on your DB schema
        raise HTTPException(status_code=400, detail=f"Invalid order_by field: {order_by}")

    # Map ordering
    ordering = text(f"{order_by} {order_direction}")  # Explicitly use SQLAlchemy's text for ordering

    offset = (page - 1) * limit

    try:
        users_query = (
            db.query(User)
            .order_by(ordering)  # Use the text expression for ordering
            .offset(offset)
            .limit(limit)
            .all()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    users_response = []
    for user in users_query:
        # Get the role and admin information
        role = db.query(Role).filter(Role.user_id == user.user_id).first()
        admin = db.query(Admin).filter(Admin.user_id == user.user_id).first()
        is_admin = bool(admin)

        custom_fields = {
            "is_active": str(user.is_active),
            "role": role.role if role else None,
            "is_admin": str(is_admin)
        }
        
        users_response.append(GetUsersResponse(user_identifier=user.username, custom_fields=custom_fields))

    return users_response


@router.get("/get-user")
async def get_user(
    username: str = Query(...),
    authorization: str = Header(...),
    x_timestamp: str = Header(...),
    db: Session = Depends(get_db),
):
    """Validate HMAC and return JWT token"""
    try:
        # Validate HMAC
        if not authorization.startswith("HMAC "):
            raise ValueError("Invalid Authorization header format")
        provided_signature = authorization.split(" ")[1]
        validate_hmac_signature(SHARED_SECRET_KEY, username, provided_signature, x_timestamp)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Fetch user from DB
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check user role
    role = db.query(Role).filter(Role.user_id == user.user_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role not assigned to user")

    # Check if user is an admin
    admin = db.query(Admin).filter(Admin.user_id == user.user_id).first()
    is_admin = bool(admin)


    jwt_token = create_access_token(data={
        "username": user.username,
        "sub": user.username,
        "role": role.role,
        "is_admin": is_admin,
        "is_active": user.is_active,
        "user_id": user.user_id
    })

    return {"access_token": jwt_token, "token_type": "bearer"}
