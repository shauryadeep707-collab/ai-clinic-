from pydantic import BaseModel
from typing import Optional, List

class MessageCreate(BaseModel):
    message_content: str

class MessageResponse(BaseModel):
    message_id: int
    consultation_id: int
    sender_role: str
    message_content: str
    is_urgent_warning: int
    timestamp: str

class ConsultationCreate(BaseModel):
    session_title: Optional[str] = "General Health Consultation"
    chief_complaint: Optional[str] = None
    initial_message: Optional[str] = None

class ConsultationDetailResponse(BaseModel):
    consultation_id: int
    patient_user_id: int
    session_title: str
    chief_complaint: Optional[str] = None
    triage_level: str
    summary: Optional[str] = None
    recommended_action: Optional[str] = None
    medical_sources_cited: Optional[str] = None
    started_at: str
    ended_at: Optional[str] = None
    messages: List[MessageResponse] = []
