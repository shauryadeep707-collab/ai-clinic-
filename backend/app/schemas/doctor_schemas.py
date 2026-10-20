from pydantic import BaseModel
from typing import Optional, List

class DoctorProfileResponse(BaseModel):
    doctor_id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    specialization: str
    qualification_summary: str
    experience_years: int
    medical_reg_number: str
    registration_council: str
    consultation_fee: float
    verification_status: str
    bio: Optional[str] = None
    rating: float
    total_reviews: int
    avatar_url: Optional[str] = None

class DoctorApplicationSubmit(BaseModel):
    specialization: str
    qualification_summary: str
    experience_years: int
    medical_reg_number: str
    registration_council: str
    consultation_fee: float
    bio: Optional[str] = None

class VerificationReviewRequest(BaseModel):
    application_id: int
    action: str # "Approved", "Rejected", "Requested Info"
    notes: Optional[str] = None
