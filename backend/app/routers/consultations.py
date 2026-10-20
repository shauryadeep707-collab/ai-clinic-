from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime
from backend.app.schemas.consultation_schemas import ConsultationCreate, MessageCreate, ConsultationDetailResponse, MessageResponse
from backend.app.database.connection import get_db
from backend.app.security.auth import get_current_user, verify_patient_access
from ai.health_assistant.assistant import get_assistant
from backend.app.services.timeline_service import timeline_service

router = APIRouter(prefix="/api/consultations", tags=["AI Health Consultations"])

@router.post("")
def create_consultation(req: ConsultationCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["user_id"]
    title = req.session_title or "General Consultation"
    complaint = req.chief_complaint or (req.initial_message[:100] if req.initial_message else "Routine Inquiry")

    consult_id = db.execute_write("""
        INSERT INTO ai_consultations (patient_user_id, session_title, chief_complaint, triage_level)
        VALUES (?, ?, ?, 'Routine')
    """, (user_id, title, complaint))

    # Add initial greeting from assistant
    db.execute_write("""
        INSERT INTO ai_consultation_messages (consultation_id, sender_role, message_content)
        VALUES (?, 'assistant', 'Hello! I am your AI health assistant. Please tell me your symptoms or health concern, and I will ask a few questions to understand better.')
    """, (consult_id,))

    # If patient sent an initial symptom in request
    if req.initial_message:
        db.execute_write("""
            INSERT INTO ai_consultation_messages (consultation_id, sender_role, message_content)
            VALUES (?, 'user', ?)
        """, (consult_id, req.initial_message))

        assistant = get_assistant()
        ai_reply = assistant.generate_consultation_reply([
            {"role": "assistant", "content": "Hello! I am your AI health assistant. Please tell me your symptoms..."},
            {"role": "user", "content": req.initial_message}
        ])

        db.execute_write("""
            INSERT INTO ai_consultation_messages (consultation_id, sender_role, message_content, is_urgent_warning)
            VALUES (?, 'assistant', ?, ?)
        """, (consult_id, ai_reply["reply"], ai_reply["is_urgent_warning"]))

        db.execute_write("""
            UPDATE ai_consultations 
            SET triage_level = ?, summary = ?, recommended_action = ?
            WHERE consultation_id = ?
        """, (ai_reply["triage_level"], ai_reply["general_guidance"], "Consult verified clinician if symptoms persist", consult_id))

    # Propagate to Timeline
    today_str = datetime.now().strftime("%Y-%m-%d")
    timeline_service.add_timeline_event(
        patient_user_id=user_id,
        event_type="AI Consultation",
        event_title="AI Health Consultation",
        event_date=today_str,
        event_time=datetime.now().strftime("%I:%M %p"),
        short_description=f"Consultation on: {complaint}",
        organization_or_doctor="AI Health Assistant",
        record_reference_id=consult_id,
        status_badge="Completed"
    )

    return {"consultation_id": consult_id, "session_title": title}

@router.get("")
def list_consultations(current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    return db.query_all("""
        SELECT * FROM ai_consultations 
        WHERE patient_user_id = ? 
        ORDER BY started_at DESC
    """, (current_user["user_id"],))

@router.get("/{consultation_id}")
def get_consultation(consultation_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    consultation = db.query_one("SELECT * FROM ai_consultations WHERE consultation_id = ?", (consultation_id,))
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    verify_patient_access(consultation["patient_user_id"], current_user)

    messages = db.query_all("""
        SELECT message_id, consultation_id, sender_role, message_content, is_urgent_warning, timestamp
        FROM ai_consultation_messages
        WHERE consultation_id = ?
        ORDER BY message_id ASC
    """, (consultation_id,))
    consultation["messages"] = messages
    return consultation

@router.post("/{consultation_id}/messages")
def send_message(consultation_id: int, req: MessageCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    db = get_db()
    consultation = db.query_one("SELECT * FROM ai_consultations WHERE consultation_id = ?", (consultation_id,))
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    verify_patient_access(consultation["patient_user_id"], current_user)

    # 1. Insert patient message
    db.execute_write("""
        INSERT INTO ai_consultation_messages (consultation_id, sender_role, message_content)
        VALUES (?, 'user', ?)
    """, (consultation_id, req.message_content))

    # 2. Fetch full conversation history
    all_msgs = db.query_all("""
        SELECT sender_role, message_content 
        FROM ai_consultation_messages 
        WHERE consultation_id = ? 
        ORDER BY message_id ASC
    """, (consultation_id,))

    history = [{"role": m["sender_role"], "content": m["message_content"]} for m in all_msgs]

    # 3. Generate clinical AI reply (with emergency rules check)
    assistant = get_assistant()
    ai_reply = assistant.generate_consultation_reply(history)

    # 4. Insert assistant message
    ai_msg_id = db.execute_write("""
        INSERT INTO ai_consultation_messages (consultation_id, sender_role, message_content, is_urgent_warning)
        VALUES (?, 'assistant', ?, ?)
    """, (consultation_id, ai_reply["reply"], ai_reply["is_urgent_warning"]))

    # 5. Update consultation triage and summary
    db.execute_write("""
        UPDATE ai_consultations 
        SET triage_level = ?, summary = ?, recommended_action = ?
        WHERE consultation_id = ?
    """, (ai_reply["triage_level"], ai_reply["general_guidance"], "Consult verified clinician", consultation_id))

    return {
        "user_message": req.message_content,
        "assistant_reply": ai_reply["reply"],
        "is_urgent_warning": ai_reply["is_urgent_warning"],
        "triage_level": ai_reply["triage_level"],
        "reported_symptoms": ai_reply["reported_symptoms"],
        "possible_causes": ai_reply["possible_causes"],
        "general_guidance": ai_reply["general_guidance"],
        "medical_sources": ai_reply["medical_sources"]
    }
