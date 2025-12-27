from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Create user request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: str = "viewer"


class UserLogin(BaseModel):
    """Login request"""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    username: str
    role: str
    full_name: Optional[str]
    is_active: bool
    created_at: str
    last_login: Optional[str]


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class APIKeyResponse(BaseModel):
    """API key response"""
    api_key: str
    user_id: str
    created_at: str