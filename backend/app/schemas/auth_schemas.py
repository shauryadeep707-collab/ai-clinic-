from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    role: str = Field("patient", pattern="^(patient|doctor)$")
    phone: Optional[str] = None
    # For doctor registration
    specialization: Optional[str] = None
    qualification_summary: Optional[str] = None
    medical_reg_number: Optional[str] = None
    registration_council: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    full_name: str
    email: str

class UserResponse(BaseModel):
    user_id: int
    email: str
    role: str
    full_name: str
    phone: Optional[str] = None
    is_active: int
    is_verified: int

class PasswordResetRequest(BaseModel):
    email: str
    new_password: str = Field(..., min_length=6)
