from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.schemas.medicine_schemas import MedicineResponse, ReminderCreate, ReminderResponse
from backend.app.security.auth import get_current_user
from backend.app.services.medicine_service import medicine_service

router = APIRouter(prefix="/api/medicines", tags=["Medicines & Reminders"])

@router.get("", response_model=List[MedicineResponse])
def search_medicines(query: Optional[str] = Query(None)):
    return medicine_service.get_medicines_catalog(query)

@router.get("/reminders", response_model=List[ReminderResponse])
def get_reminders(current_user: Dict[str, Any] = Depends(get_current_user)):
    return medicine_service.get_patient_reminders(current_user["user_id"])

@router.post("/reminders", response_model=ReminderResponse)
def add_reminder(req: ReminderCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    return medicine_service.create_reminder(
        patient_user_id=current_user["user_id"],
        medicine_name=req.medicine_name,
        dosage=req.dosage,
        reminder_time=req.reminder_time,
        days_of_week=req.days_of_week or "Daily",
        start_date=req.start_date
    )

@router.put("/reminders/{reminder_id}/toggle", response_model=ReminderResponse)
def toggle_reminder(reminder_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    updated = medicine_service.toggle_reminder(reminder_id, current_user["user_id"])
    if not updated:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return updated

@router.post("/allergy-check")
def check_allergy(medicine_name: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    return medicine_service.check_patient_allergies_and_interactions(current_user["user_id"], medicine_name)

@router.get("/{medicine_id}", response_model=MedicineResponse)
def get_medicine(medicine_id: int):
    med = medicine_service.get_medicine_by_id(medicine_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return med
