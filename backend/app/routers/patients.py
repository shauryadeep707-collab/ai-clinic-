from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from backend.app.schemas.patient_schemas import PatientProfileResponse, PatientProfileUpdate, HealthObservationCreate
from backend.app.database.connection import get_db
from backend.app.security.auth import get_current_user, require_role
from backend.app.services.timeline_service import timeline_service

router = APIRouter(prefix="/api/patients", tags=["Patient Profiles"])

@router.get("/profile", response_model=PatientProfileResponse)
def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["user_id"]
    profile = db.query_one("""
        SELECT p.patient_id, p.user_id, u.full_name, u.email, u.phone, p.date_of_birth,
               p.gender, p.blood_group, p.emergency_contact_name, p.emergency_contact_phone,
               p.known_allergies, p.chronic_conditions, p.current_medications
        FROM users u
        LEFT JOIN patient_profiles p ON u.user_id = p.user_id
        WHERE u.user_id = ?
    """, (user_id,))
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile

@router.put("/profile")
def update_profile(req: PatientProfileUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["user_id"]
    
    if req.full_name or req.phone:
        db.execute_write(
            "UPDATE users SET full_name = COALESCE(?, full_name), phone = COALESCE(?, phone), updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (req.full_name, req.phone, user_id)
        )
    
    db.execute_write("""
        UPDATE patient_profiles 
        SET date_of_birth = COALESCE(?, date_of_birth),
            gender = COALESCE(?, gender),
            blood_group = COALESCE(?, blood_group),
            emergency_contact_name = COALESCE(?, emergency_contact_name),
            emergency_contact_phone = COALESCE(?, emergency_contact_phone),
            known_allergies = COALESCE(?, known_allergies),
            chronic_conditions = COALESCE(?, chronic_conditions),
            current_medications = COALESCE(?, current_medications)
        WHERE user_id = ?
    """, (
        req.date_of_birth, req.gender, req.blood_group,
        req.emergency_contact_name, req.emergency_contact_phone,
        req.known_allergies, req.chronic_conditions, req.current_medications,
        user_id
    ))
    return {"message": "Profile updated successfully"}

@router.get("/dashboard-summary")
def get_dashboard_summary(current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["user_id"]

    # Recent 3 Reports
    recent_reports = db.query_all("""
        SELECT report_id, report_title, report_category, test_name, test_date, upload_date
        FROM medical_reports 
        WHERE patient_user_id = ?
        ORDER BY test_date DESC, report_id DESC
        LIMIT 3
    """, (user_id,))

    # Upcoming Appointments
    upcoming_appointments = db.query_all("""
        SELECT a.appointment_id, a.doctor_id, u.full_name as doctor_name, d.specialization,
               a.appointment_date, a.appointment_time, a.consultation_type, a.status
        FROM appointments a
        JOIN doctor_profiles d ON a.doctor_id = d.doctor_id
        JOIN users u ON d.user_id = u.user_id
        WHERE a.patient_user_id = ? AND a.status != 'Cancelled'
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
        LIMIT 2
    """, (user_id,))

    # Active Medicine Reminders
    reminders = db.query_all("""
        SELECT reminder_id, medicine_name, dosage, reminder_time, days_of_week
        FROM medicine_reminders
        WHERE patient_user_id = ? AND is_active = 1
        LIMIT 3
    """, (user_id,))

    return {
        "user_name": current_user["full_name"],
        "recent_reports": recent_reports,
        "upcoming_appointments": upcoming_appointments,
        "active_reminders": reminders
    }

@router.post("/observations")
def add_observation(req: HealthObservationCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["user_id"]
    obs_id = db.execute_write("""
        INSERT INTO patient_health_observations (patient_user_id, observation_date, observation_type, measured_value, unit, notes)
        VALUES (?, COALESCE(?, CURRENT_DATE), ?, ?, ?, ?)
    """, (user_id, req.observation_date, req.observation_type, req.measured_value, req.unit or "", req.notes or ""))

    # Propagate to Timeline
    timeline_service.add_timeline_event(
        patient_user_id=user_id,
        event_type="Health Observation",
        event_title=f"{req.observation_type} Log",
        event_date=req.observation_date or "2024-10-18",
        short_description=f"Recorded: {req.measured_value} {req.unit or ''}. Notes: {req.notes or 'None'}",
        organization_or_doctor="Patient Self-Log",
        record_reference_id=obs_id,
        status_badge="Recorded"
    )

    return {"message": "Health observation saved", "observation_id": obs_id}

@router.get("/observations")
def list_observations(current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    return db.query_all("""
        SELECT * FROM patient_health_observations 
        WHERE patient_user_id = ? 
        ORDER BY observation_date DESC
    """, (current_user["user_id"],))
