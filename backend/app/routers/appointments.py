from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from backend.app.schemas.appointment_schemas import AppointmentCreate, AppointmentResponse
from backend.app.security.auth import get_current_user
from backend.app.services.appointment_service import appointment_service
from backend.app.services.doctor_service import doctor_service

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

@router.get("")
def list_appointments(current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["user_id"]
    if current_user["role"] == "doctor":
        doc = doctor_service.get_doctor_by_user_id(user_id)
        if not doc:
            return []
        return appointment_service.get_doctor_appointments(doc["doctor_id"])
    else:
        return appointment_service.get_patient_appointments(user_id)

@router.post("")
def book_appointment(req: AppointmentCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        appt = appointment_service.book_appointment(
            patient_user_id=user_id,
            doctor_id=req.doctor_id,
            appointment_date=req.appointment_date,
            appointment_time=req.appointment_time,
            consultation_type=req.consultation_type,
            reason=req.reason_for_visit
        )
        return appt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    appointment_service.update_appointment_status(appointment_id, "Cancelled")
    return {"message": "Appointment cancelled successfully."}

@router.put("/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    doctor_notes: str = "",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    appointment_service.update_appointment_status(appointment_id, "Completed", doctor_notes)
    return {"message": "Appointment marked as completed."}
