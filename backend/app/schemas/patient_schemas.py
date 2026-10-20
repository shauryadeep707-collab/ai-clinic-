from pydantic import BaseModel
from typing import Optional

class PatientProfileResponse(BaseModel):
    patient_id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    known_allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None

class PatientProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    known_allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None

class HealthObservationCreate(BaseModel):
    observation_type: str # 'Blood Pressure', 'Blood Glucose', 'Weight', 'Temperature', 'Symptom'
    measured_value: str
    unit: Optional[str] = None
    notes: Optional[str] = None
    observation_date: Optional[str] = None
