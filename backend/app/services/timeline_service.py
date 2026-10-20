from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.database.connection import get_db

class TimelineService:
    @staticmethod
    def add_timeline_event(
        patient_user_id: int,
        event_type: str,
        event_title: str,
        event_date: str,
        event_time: Optional[str] = None,
        short_description: Optional[str] = None,
        organization_or_doctor: Optional[str] = None,
        record_reference_id: Optional[int] = None,
        status_badge: str = "Completed"
    ) -> int:
        db = get_db()
        sql = """
            INSERT INTO health_timeline_events 
            (patient_user_id, event_type, event_title, event_date, event_time, short_description, organization_or_doctor, record_reference_id, status_badge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return db.execute_write(sql, (
            patient_user_id, event_type, event_title, event_date, event_time,
            short_description, organization_or_doctor, record_reference_id, status_badge
        ))

    @staticmethod
    def get_patient_timeline(
        patient_user_id: int,
        event_type: Optional[str] = None,
        search_query: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        db = get_db()
        conditions = ["patient_user_id = ?"]
        params = [patient_user_id]

        if event_type and event_type.lower() != "all":
            conditions.append("event_type = ?")
            params.append(event_type)

        if search_query:
            conditions.append("(event_title LIKE ? OR short_description LIKE ? OR organization_or_doctor LIKE ?)")
            q = f"%{search_query}%"
            params.extend([q, q, q])

        if date_from:
            conditions.append("event_date >= ?")
            params.append(date_from)

        if date_to:
            conditions.append("event_date <= ?")
            params.append(date_to)

        order_dir = "ASC" if sort_order.lower() == "asc" else "DESC"
        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT event_id, patient_user_id, event_type, event_title, event_date, event_time, 
                   short_description, organization_or_doctor, record_reference_id, status_badge, created_at
            FROM health_timeline_events
            WHERE {where_clause}
            ORDER BY event_date {order_dir}, event_id {order_dir}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        return db.query_all(sql, tuple(params))

    @staticmethod
    def get_event_detail(event_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        event = db.query_one("SELECT * FROM health_timeline_events WHERE event_id = ?", (event_id,))
        if not event:
            return None

        # Fetch linked source record
        ref_id = event.get("record_reference_id")
        event_type = event.get("event_type")
        source_detail = None

        if ref_id:
            if "Report" in event_type:
                source_detail = db.query_one("SELECT * FROM medical_reports WHERE report_id = ?", (ref_id,))
                if source_detail:
                    source_detail["ai_summary"] = db.query_one("SELECT * FROM report_summaries WHERE report_id = ?", (ref_id,))
                    source_detail["measurements"] = db.query_all("SELECT * FROM report_extracted_measurements WHERE report_id = ?", (ref_id,))
            elif "Consultation" in event_type:
                source_detail = db.query_one("SELECT * FROM ai_consultations WHERE consultation_id = ?", (ref_id,))
                if source_detail:
                    source_detail["messages"] = db.query_all("SELECT * FROM ai_consultation_messages WHERE consultation_id = ?", (ref_id,))
            elif "Appointment" in event_type or "Doctor" in event_type:
                source_detail = db.query_one("""
                    SELECT a.*, d.specialization, u.full_name as doctor_name 
                    FROM appointments a 
                    JOIN doctor_profiles d ON a.doctor_id = d.doctor_id
                    JOIN users u ON d.user_id = u.user_id
                    WHERE a.appointment_id = ?
                """, (ref_id,))

        event["source_detail"] = source_detail
        return event

timeline_service = TimelineService()
