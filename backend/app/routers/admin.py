from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from backend.app.schemas.doctor_schemas import VerificationReviewRequest
from backend.app.database.connection import get_db
from backend.app.security.auth import require_role
from backend.app.services.doctor_service import doctor_service

router = APIRouter(prefix="/api/admin", tags=["Administrator Dashboard"])

@router.get("/doctors/verification-queue")
def get_verification_queue(
    status: str = "Pending",
    admin_user: Dict[str, Any] = Depends(require_role(["admin"]))
):
    return doctor_service.get_admin_verification_queue(status)

@router.post("/doctors/review")
def review_doctor(
    req: VerificationReviewRequest,
    admin_user: Dict[str, Any] = Depends(require_role(["admin"]))
):
    success = doctor_service.review_doctor_application(
        application_id=req.application_id,
        action=req.action,
        admin_user_id=admin_user["user_id"],
        notes=req.notes
    )
    if not success:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": f"Application successfully updated with decision: {req.action}"}

@router.get("/stats")
def get_admin_stats(admin_user: Dict[str, Any] = Depends(require_role(["admin"]))):
    db = get_db()
    total_users = db.query_one("SELECT COUNT(*) as count FROM users")
    patients = db.query_one("SELECT COUNT(*) as count FROM users WHERE role = 'patient'")
    doctors = db.query_one("SELECT COUNT(*) as count FROM users WHERE role = 'doctor'")
    pending_apps = db.query_one("SELECT COUNT(*) as count FROM doctor_applications WHERE status = 'Pending'")
    approved_apps = db.query_one("SELECT COUNT(*) as count FROM doctor_applications WHERE status = 'Verified'")
    rejected_apps = db.query_one("SELECT COUNT(*) as count FROM doctor_applications WHERE status = 'Rejected'")
    reports_count = db.query_one("SELECT COUNT(*) as count FROM medical_reports")

    return {
        "total_users": total_users["count"] if total_users else 0,
        "patients_count": patients["count"] if patients else 0,
        "doctors_count": doctors["count"] if doctors else 0,
        "pending_applications": pending_apps["count"] if pending_apps else 0,
        "approved_applications": approved_apps["count"] if approved_apps else 0,
        "rejected_applications": rejected_apps["count"] if rejected_apps else 0,
        "reports_processed": reports_count["count"] if reports_count else 0
    }

@router.get("/audit-logs")
def get_audit_logs(admin_user: Dict[str, Any] = Depends(require_role(["admin"]))):
    db = get_db()
    return db.query_all("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50")
