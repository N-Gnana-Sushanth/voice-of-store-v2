"""Authentication and user request/response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Plaintext user password")


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    store_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserResponse


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Argon2id-hashed user password")
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(default="analyst", description="admin, store_manager, or analyst")
    store_id: Optional[str] = Field(default=None, description="Required for store_manager role")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    store_id: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)
