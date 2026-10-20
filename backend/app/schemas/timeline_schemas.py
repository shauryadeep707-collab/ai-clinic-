from pydantic import BaseModel
from typing import Optional

class TimelineEventResponse(BaseModel):
    event_id: int
    patient_user_id: int
    event_type: str
    event_title: str
    event_date: str
    event_time: Optional[str] = None
    short_description: Optional[str] = None
    organization_or_doctor: Optional[str] = None
    record_reference_id: Optional[int] = None
    status_badge: str
    created_at: str
