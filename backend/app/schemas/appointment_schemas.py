from pydantic import BaseModel
from typing import Optional

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: str # YYYY-MM-DD
    appointment_time: str # e.g. "11:00 AM"
    consultation_type: str = "Online" # "Online" or "In-Person"
    reason_for_visit: Optional[str] = None

class AppointmentResponse(BaseModel):
    appointment_id: int
    patient_user_id: int
    doctor_id: int
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    patient_name: Optional[str] = None
    appointment_date: str
    appointment_time: str
    consultation_type: str
    status: str
    reason_for_visit: Optional[str] = None
    doctor_notes: Optional[str] = None
    created_at: str

class AvailabilityResponse(BaseModel):
    doctor_id: int
    available_dates: list
    slots: list
