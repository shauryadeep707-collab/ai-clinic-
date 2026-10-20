from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.database.connection import get_db

class DoctorService:
    @staticmethod
    def get_verified_doctors(specialization: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        db = get_db()
        sql = """
            SELECT d.doctor_id, d.user_id, u.full_name, u.email, u.phone, d.specialization,
                   d.qualification_summary, d.experience_years, d.medical_reg_number,
                   d.registration_council, d.consultation_fee, d.verification_status,
                   d.bio, d.rating, d.total_reviews, d.avatar_url
            FROM doctor_profiles d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.verification_status = 'Verified'
        """
        params = []
        if specialization and specialization.lower() != "all":
            sql += " AND LOWER(d.specialization) = LOWER(?)"
            params.append(specialization)
        if search:
            sql += " AND (LOWER(u.full_name) LIKE ? OR LOWER(d.specialization) LIKE ?)"
            s = f"%{search.lower()}%"
            params.extend([s, s])
        
        sql += " ORDER BY d.rating DESC, d.experience_years DESC"
        return db.query_all(sql, tuple(params))

    @staticmethod
    def get_doctor_by_id(doctor_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        sql = """
            SELECT d.doctor_id, d.user_id, u.full_name, u.email, u.phone, d.specialization,
                   d.qualification_summary, d.experience_years, d.medical_reg_number,
                   d.registration_council, d.consultation_fee, d.verification_status,
                   d.bio, d.rating, d.total_reviews, d.avatar_url
            FROM doctor_profiles d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.doctor_id = ?
        """
        return db.query_one(sql, (doctor_id,))

    @staticmethod
    def get_doctor_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        sql = """
            SELECT d.doctor_id, d.user_id, u.full_name, u.email, u.phone, d.specialization,
                   d.qualification_summary, d.experience_years, d.medical_reg_number,
                   d.registration_council, d.consultation_fee, d.verification_status,
                   d.bio, d.rating, d.total_reviews, d.avatar_url
            FROM doctor_profiles d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.user_id = ?
        """
        return db.query_one(sql, (user_id,))

    @staticmethod
    def get_doctor_dashboard_stats(doctor_id: int) -> Dict[str, Any]:
        db = get_db()
        # Today's appointments count
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_appts = db.query_all("""
            SELECT a.appointment_id, u.full_name as patient_name, a.appointment_time, 
                   a.consultation_type, a.status, a.reason_for_visit
            FROM appointments a
            JOIN users u ON a.patient_user_id = u.user_id
            WHERE a.doctor_id = ?
            ORDER BY a.appointment_time ASC
        """, (doctor_id,))

        total_patients = db.query_one("""
            SELECT COUNT(DISTINCT patient_user_id) as count 
            FROM appointments WHERE doctor_id = ?
        """, (doctor_id,))

        pending_reports = db.query_one("""
            SELECT COUNT(*) as count FROM medical_reports
        """)

        recent_reports = db.query_all("""
            SELECT r.report_id, r.report_title, u.full_name as patient_name, r.test_date, r.report_category
            FROM medical_reports r
            JOIN users u ON r.patient_user_id = u.user_id
            ORDER BY r.test_date DESC LIMIT 5
        """)

        return {
            "today_appointments_count": len(today_appts),
            "today_appointments": today_appts,
            "total_patients": total_patients["count"] if total_patients else 0,
            "new_patients": 6,
            "pending_reports_count": pending_reports["count"] if pending_reports else 0,
            "recent_patient_reports": recent_reports
        }

    @staticmethod
    def get_admin_verification_queue(status_filter: str = "Pending") -> List[Dict[str, Any]]:
        db = get_db()
        sql = """
            SELECT a.application_id, a.doctor_id, u.full_name as applicant_name, u.email,
                   d.specialization, d.qualification_summary, d.experience_years,
                   d.medical_reg_number, d.registration_council, a.status, a.submitted_on,
                   a.review_notes
            FROM doctor_applications a
            JOIN doctor_profiles d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
        """
        params = []
        if status_filter and status_filter.lower() != "all":
            sql += " WHERE LOWER(a.status) = LOWER(?)"
            params.append(status_filter)
        sql += " ORDER BY a.submitted_on DESC"
        return db.query_all(sql, tuple(params))

    @staticmethod
    def review_doctor_application(application_id: int, action: str, admin_user_id: int, notes: Optional[str] = None) -> bool:
        db = get_db()
        app = db.query_one("SELECT * FROM doctor_applications WHERE application_id = ?", (application_id,))
        if not app:
            return False

        new_status = "Verified" if action.lower() == "approved" else ("Rejected" if action.lower() == "rejected" else "Additional info required")
        
        # Update application status
        db.execute_write("""
            UPDATE doctor_applications 
            SET status = ?, reviewed_by_admin_id = ?, review_notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE application_id = ?
        """, (new_status, admin_user_id, notes or "", application_id))

        # Update doctor profile verification status
        db.execute_write("""
            UPDATE doctor_profiles 
            SET verification_status = ?
            WHERE doctor_id = ?
        """, (new_status, app["doctor_id"]))

        # Also update users is_verified
        doc_profile = db.query_one("SELECT user_id FROM doctor_profiles WHERE doctor_id = ?", (app["doctor_id"],))
        if doc_profile:
            is_ver_val = 1 if new_status == "Verified" else 0
            db.execute_write("UPDATE users SET is_verified = ? WHERE user_id = ?", (is_ver_val, doc_profile["user_id"]))

        # Log audit trail
        db.execute_write("""
            INSERT INTO doctor_verification_reviews (application_id, admin_user_id, action_taken, reason_description)
            VALUES (?, ?, ?, ?)
        """, (application_id, admin_user_id, action, notes or ""))

        return True

doctor_service = DoctorService()
