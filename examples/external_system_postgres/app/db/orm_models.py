from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Role(Base):
    __tablename__ = "roles_list"
    role_id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
