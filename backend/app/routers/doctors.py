from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Dict, Any, List, Optional
from backend.app.schemas.doctor_schemas import DoctorProfileResponse, DoctorApplicationSubmit
from backend.app.database.connection import get_db
from backend.app.security.auth import get_current_user, require_role
from backend.app.services.doctor_service import doctor_service

router = APIRouter(prefix="/api/doctors", tags=["Doctors & Verification"])

@router.get("", response_model=List[DoctorProfileResponse])
def list_doctors(
    specialization: Optional[str] = None,
    search: Optional[str] = None
):
    return doctor_service.get_verified_doctors(specialization, search)

@router.get("/dashboard/stats")
def get_doctor_dashboard(current_user: Dict[str, Any] = Depends(require_role(["doctor", "admin"]))):
    user_id = current_user["user_id"]
    doc = doctor_service.get_doctor_by_user_id(user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor profile not found for this account.")
    return doctor_service.get_doctor_dashboard_stats(doc["doctor_id"])

@router.get("/{doctor_id}", response_model=DoctorProfileResponse)
def get_doctor_profile(doctor_id: int):
    doc = doctor_service.get_doctor_by_id(doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doc

@router.post("/applications")
def submit_application(
    req: DoctorApplicationSubmit,
    current_user: Dict[str, Any] = Depends(require_role(["doctor", "admin"]))
):
    db = get_db()
    user_id = current_user["user_id"]
    existing_doc = doctor_service.get_doctor_by_user_id(user_id)
    
    if existing_doc:
        doc_id = existing_doc["doctor_id"]
        db.execute_write("""
            UPDATE doctor_profiles 
            SET specialization = ?, qualification_summary = ?, experience_years = ?,
                medical_reg_number = ?, registration_council = ?, consultation_fee = ?,
                bio = ?, verification_status = 'Pending', updated_at = CURRENT_TIMESTAMP
            WHERE doctor_id = ?
        """, (
            req.specialization, req.qualification_summary, req.experience_years,
            req.medical_reg_number, req.registration_council, req.consultation_fee,
            req.bio or "", doc_id
        ))
    else:
        doc_id = db.execute_write("""
            INSERT INTO doctor_profiles 
            (user_id, specialization, qualification_summary, experience_years, medical_reg_number, registration_council, consultation_fee, verification_status, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
        """, (
            user_id, req.specialization, req.qualification_summary, req.experience_years,
            req.medical_reg_number, req.registration_council, req.consultation_fee, req.bio or ""
        ))

    # Create application record
    app_id = db.execute_write("""
        INSERT INTO doctor_applications (doctor_id, status)
        VALUES (?, 'Pending')
    """, (doc_id,))

    return {
        "message": "Doctor verification application submitted successfully.",
        "application_id": app_id,
        "status": "Pending"
    }
