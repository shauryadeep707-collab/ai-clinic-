from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.database.connection import get_db
from backend.app.services.timeline_service import timeline_service

class AppointmentService:
    @staticmethod
    def get_patient_appointments(patient_user_id: int) -> List[Dict[str, Any]]:
        db = get_db()
        sql = """
            SELECT a.appointment_id, a.patient_user_id, a.doctor_id, u.full_name as doctor_name,
                   d.specialization as doctor_specialization, a.appointment_date, a.appointment_time,
                   a.consultation_type, a.status, a.reason_for_visit, a.doctor_notes, a.created_at
            FROM appointments a
            JOIN doctor_profiles d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.patient_user_id = ?
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        return db.query_all(sql, (patient_user_id,))

    @staticmethod
    def get_doctor_appointments(doctor_id: int) -> List[Dict[str, Any]]:
        db = get_db()
        sql = """
            SELECT a.appointment_id, a.patient_user_id, a.doctor_id, u.full_name as patient_name,
                   u.email as patient_email, u.phone as patient_phone, a.appointment_date,
                   a.appointment_time, a.consultation_type, a.status, a.reason_for_visit,
                   a.doctor_notes, a.created_at
            FROM appointments a
            JOIN users u ON a.patient_user_id = u.user_id
            WHERE a.doctor_id = ?
            ORDER BY a.appointment_date ASC, a.appointment_time ASC
        """
        return db.query_all(sql, (doctor_id,))

    @staticmethod
    def book_appointment(
        patient_user_id: int,
        doctor_id: int,
        appointment_date: str,
        appointment_time: str,
        consultation_type: str = "Online",
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        db = get_db()
        # Prevent double booking conflict
        conflict = db.query_one("""
            SELECT appointment_id FROM appointments
            WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ? AND status != 'Cancelled'
        """, (doctor_id, appointment_date, appointment_time))
        if conflict:
            raise ValueError("This doctor already has a confirmed booking for the selected date and time slot.")

        appt_id = db.execute_write("""
            INSERT INTO appointments 
            (patient_user_id, doctor_id, appointment_date, appointment_time, consultation_type, status, reason_for_visit)
            VALUES (?, ?, ?, ?, ?, 'Confirmed', ?)
        """, (patient_user_id, doctor_id, appointment_date, appointment_time, consultation_type, reason or "Consultation"))

        # Fetch doctor details for timeline event
        doctor = db.query_one("""
            SELECT u.full_name, d.specialization 
            FROM doctor_profiles d 
            JOIN users u ON d.user_id = u.user_id 
            WHERE d.doctor_id = ?
        """, (doctor_id,))
        doc_name = doctor["full_name"] if doctor else "Doctor"

        # Propagate to Unified Health Timeline
        timeline_service.add_timeline_event(
            patient_user_id=patient_user_id,
            event_type="Doctor Consultation",
            event_title=f"Appointment with {doc_name}",
            event_date=appointment_date,
            event_time=appointment_time,
            short_description=f"{consultation_type} consultation: {reason or 'General checkup'}",
            organization_or_doctor=doc_name,
            record_reference_id=appt_id,
            status_badge="Confirmed"
        )

        return db.query_one("""
            SELECT a.*, u.full_name as doctor_name, d.specialization as doctor_specialization
            FROM appointments a
            JOIN doctor_profiles d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.appointment_id = ?
        """, (appt_id,))

    @staticmethod
    def update_appointment_status(appointment_id: int, status: str, doctor_notes: Optional[str] = None) -> bool:
        db = get_db()
        sql = "UPDATE appointments SET status = ?"
        params = [status]
        if doctor_notes:
            sql += ", doctor_notes = ?"
            params.append(doctor_notes)
        sql += " WHERE appointment_id = ?"
        params.append(appointment_id)
        db.execute_write(sql, tuple(params))
        return True

appointment_service = AppointmentService()
