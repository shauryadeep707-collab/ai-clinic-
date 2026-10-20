from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.database.connection import get_db
from backend.app.security.auth import get_current_user, verify_patient_access
from backend.app.services.timeline_service import timeline_service

router = APIRouter(prefix="/api/timeline", tags=["Unified Health Timeline"])

@router.get("")
def get_timeline(
    event_type: Optional[str] = Query(None, description="Event type filter e.g. Report Upload, AI Consultation, Doctor Consultation"),
    search: Optional[str] = Query(None, description="Search keyword in event title or doctor"),
    date_from: Optional[str] = Query(None, description="From Date YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="To Date YYYY-MM-DD"),
    sort: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    return timeline_service.get_patient_timeline(
        patient_user_id=user_id,
        event_type=event_type,
        search_query=search,
        date_from=date_from,
        date_to=date_to,
        sort_order=sort,
        limit=limit,
        offset=offset
    )

@router.get("/{event_id}")
def get_timeline_event_detail(event_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    event = timeline_service.get_event_detail(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    verify_patient_access(event["patient_user_id"], current_user)
    return event
