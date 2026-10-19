from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserMeResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMeResponse

class ValidateInviteResponse(BaseModel):
    is_valid: bool
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    course_track: Optional[str] = None
    message: str

class ActivateAccountRequest(BaseModel):
    token: str = Field(..., min_length=10)
    password: str = Field(..., min_length=8)
