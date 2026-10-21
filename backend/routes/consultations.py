"""
Consultations route for AI Health Assistant.
Implements the consultation request workflow between patients and doctors.
Includes FIFO queue for pending doctor requests, idempotent client_id,
consent tracking, and status transitions with in-app notifications.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, g
from backend import db as database
from backend.auth_utils import role_required, get_current_user
from backend.services.notification_service import create_notification

consultations_bp = Blueprint('consultations', __name__)

# Valid state transitions: status can never move backwards
ALLOWED_TRANSITIONS = {
    'pending': ['accepted', 'declined'],
    'accepted': ['completed'],
    'declined': [],
    'completed': []
}

@consultations_bp.route('/api/consultations', methods=['POST'])
def request_consultation():
    """
    Handles both AI consultation session creation (clinic frontend)
    and doctor consultation requests (bestproject).
    """
    user = get_current_user()
    patient_id = user['id'] if user else 18
    data = request.get_json() or {}

    # If this is an AI consultation session start
    if 'session_title' in data or not data.get('doctor_id'):
        title = data.get('session_title', 'General Health Assessment')
        assessment_id = database.insert(
            g.db,
            "INSERT INTO assessments (patient_id, status, category, summary) VALUES (?, 'in_progress', 'general', ?)",
            (patient_id, title)
        )
        return jsonify({
            'ok': True,
            'consultation_id': assessment_id,
            'id': assessment_id,
            'session_title': title,
            'status': 'in_progress'
        }), 201

    # Doctor consultation request workflow
    if not user:
        return jsonify({'ok': False, 'error': 'Please log in'}), 401

    assessment_id = data.get('assessment_id')
    doctor_id = data.get('doctor_id')
    client_id = data.get('client_id')
    consent_given = 1 if data.get('consent_given', False) else 0

    if not assessment_id or not doctor_id:
        return jsonify({'ok': False, 'error': 'Assessment ID and Doctor ID are required'}), 400

    if not consent_given:
        return jsonify({'ok': False, 'error': 'Patient consent is required to share health data with the doctor'}), 400

    # Idempotent check
    if client_id:
        existing = database.fetch_one(g.db, "SELECT * FROM consultations WHERE client_id = ?", (client_id,))
        if existing:
            return jsonify({'ok': True, 'data': existing}), 200

    # Verify doctor exists and is verified
    doctor = database.fetch_one(g.db, "SELECT id, name FROM users WHERE id = ? AND role = 'doctor' AND is_verified = 1", (doctor_id,))
    if not doctor:
        return jsonify({'ok': False, 'error': 'Selected doctor is not available'}), 404

    # Verify assessment belongs to this patient
    assessment = database.fetch_one(
        g.db,
        "SELECT id FROM assessments WHERE id = ? AND patient_id = ?",
        (assessment_id, user['id'])
    )
    if not assessment:
        return jsonify({'ok': False, 'error': 'Assessment not found'}), 404

    consent_at = datetime.utcnow().isoformat()
    consultation_id = database.insert(
        g.db,
        """INSERT INTO consultations 
           (client_id, assessment_id, patient_id, doctor_id, status, consent_given, consent_at) 
           VALUES (?, ?, ?, ?, 'pending', ?, ?)""",
        (client_id, assessment_id, user['id'], doctor_id, consent_given, consent_at)
    )

    is_urgent = bool(data.get('is_urgent', False))
    doctor_notice = f"🚨 URGENT HIGH-RISK ALERT from {user['name']}: Immediate medical evaluation requested!" if is_urgent else f"New consultation request from {user['name']}."

    # In-app notification to the doctor (conceptual FIFO queue)
    create_notification(
        g.db,
        user_id=doctor_id,
        text=doctor_notice,
        link=f"/pages/doctor-consultation.html?id={consultation_id}"
    )

    if is_urgent:
        create_notification(
            g.db,
            user_id=user['id'],
            text=f"🚨 Emergency consultation alert sent to Dr. {doctor['name']}. You will be alerted the moment they respond.",
            link=f"/pages/consultations.html"
        )

    return jsonify({
        'ok': True,
        'data': {
            'id': consultation_id,
            'client_id': client_id,
            'status': 'pending',
            'is_urgent': is_urgent,
            'message': 'Urgent alert sent to doctor.' if is_urgent else 'Consultation request sent to doctor.'
        }
    }), 201

@consultations_bp.route('/api/consultations', methods=['GET'])
@role_required('patient', 'doctor')
def list_consultations(user):
    """
    List consultations for the current user.
    - If Doctor: FIFO queue (pending requests ordered oldest-first, then accepted/completed).
    - If Patient: sorted by updated_at / created_at DESC.
    """
    if user['role'] == 'doctor':
        # FIFO Queue: Order pending consultations oldest-first (created_at ASC)
        consultations = database.fetch_all(
            g.db,
            """SELECT c.*, u.name as patient_name, u.email as patient_email,
                      a.category, a.risk_level, a.summary
               FROM consultations c
               JOIN users u ON c.patient_id = u.id
               JOIN assessments a ON c.assessment_id = a.id
               WHERE c.doctor_id = ?
               ORDER BY 
                 CASE WHEN c.status = 'pending' THEN 0 ELSE 1 END,
                 CASE WHEN c.status = 'pending' THEN c.created_at END ASC,
                 c.updated_at DESC""",
            (user['id'],)
        )
    else:
        # Patient's consultations
        consultations = database.fetch_all(
            g.db,
            """SELECT c.*, u.name as doctor_name, d.specialization, d.clinic_name, d.fee
               FROM consultations c
               JOIN users u ON c.doctor_id = u.id
               JOIN doctor_profiles d ON u.id = d.user_id
               WHERE c.patient_id = ?
               ORDER BY c.created_at DESC""",
            (user['id'],)
        )

    return jsonify({'ok': True, 'data': consultations})

@consultations_bp.route('/api/consultations/<int:consultation_id>', methods=['GET'])
@role_required('patient', 'doctor')
def get_consultation(user, consultation_id):
    """
    Get full details of a consultation.
    Role check: Patient can only view their own; Doctor can only view assigned.
    """
    consultation = database.fetch_one(
        g.db,
        "SELECT * FROM consultations WHERE id = ?",
        (consultation_id,)
    )
    if not consultation:
        return jsonify({'ok': False, 'error': 'Consultation not found'}), 404

    if user['role'] == 'patient' and consultation['patient_id'] != user['id']:
        return jsonify({'ok': False, 'error': 'Access denied'}), 403

    if user['role'] == 'doctor' and consultation['doctor_id'] != user['id']:
        return jsonify({'ok': False, 'error': 'Access denied'}), 403

    # Fetch patient details
    patient = database.fetch_one(
        g.db,
        """SELECT u.id, u.name, u.email, u.phone, p.age, p.gender, p.chronic_conditions, p.allergies
           FROM users u
           LEFT JOIN patient_profiles p ON u.id = p.user_id
           WHERE u.id = ?""",
        (consultation['patient_id'],)
    )

    # Fetch doctor details
    doctor = database.fetch_one(
        g.db,
        """SELECT u.id, u.name, u.email, d.specialization, d.clinic_name, d.address, d.city, d.fee
           FROM users u
           LEFT JOIN doctor_profiles d ON u.id = d.user_id
           WHERE u.id = ?""",
        (consultation['doctor_id'],)
    )

    # Fetch assessment and chat transcript
    assessment = database.fetch_one(
        g.db,
        "SELECT * FROM assessments WHERE id = ?",
        (consultation['assessment_id'],)
    )
    messages = []
    if assessment:
        assessment = dict(assessment)
        import json
        try:
            assessment['structured_json'] = json.loads(assessment.get('structured_json') or '{}')
        except (json.JSONDecodeError, TypeError):
            assessment['structured_json'] = {}
        try:
            assessment['risk_reasons'] = json.loads(assessment.get('risk_reasons') or '[]')
        except (json.JSONDecodeError, TypeError):
            assessment['risk_reasons'] = []

        messages = database.fetch_all(
            g.db,
            "SELECT role, content, created_at FROM messages WHERE assessment_id = ? ORDER BY created_at ASC",
            (assessment['id'],)
        )

    return jsonify({
        'ok': True,
        'data': {
            'consultation': consultation,
            'patient': patient,
            'doctor': doctor,
            'assessment': assessment,
            'messages': messages
        }
    })

@consultations_bp.route('/api/consultations/<int:consultation_id>/status', methods=['PUT'])
@role_required('doctor')
def update_consultation_status(user, consultation_id):
    """
    Doctor updates consultation status (accept, decline, complete) and provides advice.
    Conflict Rule: Status cannot move backwards.
    """
    consultation = database.fetch_one(
        g.db,
        "SELECT * FROM consultations WHERE id = ? AND doctor_id = ?",
        (consultation_id, user['id'])
    )
    if not consultation:
        return jsonify({'ok': False, 'error': 'Consultation not found'}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    doctor_advice = data.get('doctor_advice')

    current_status = consultation['status']

    if new_status and new_status != current_status:
        # Check allowed transition
        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            return jsonify({
                'ok': False, 
                'error': f"Illegal status transition: cannot change from '{current_status}' to '{new_status}'"
            }), 400
    else:
        new_status = current_status

    advice_to_save = doctor_advice if doctor_advice is not None else consultation.get('doctor_advice')

    database.execute(
        g.db,
        """UPDATE consultations 
           SET status = ?, doctor_advice = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ?""",
        (new_status, advice_to_save, consultation_id)
    )

    # Notify patient about the update
    status_text = {
        'accepted': f"Dr. {user['name']} accepted your consultation request.",
        'declined': f"Dr. {user['name']} declined your consultation request.",
        'completed': f"Dr. {user['name']} completed your consultation and provided medical advice."
    }.get(new_status, f"Consultation status updated to {new_status}.")

    create_notification(
        g.db,
        user_id=consultation['patient_id'],
        text=status_text,
        link=f"/pages/consultations.html"
    )

    return jsonify({
        'ok': True,
        'data': {
            'id': consultation_id,
            'status': new_status,
            'doctor_advice': advice_to_save,
            'message': 'Consultation updated successfully'
        }
    })


@consultations_bp.route('/api/consultations/<int:consultation_id>/messages', methods=['POST'])
def consultation_messages(consultation_id):
    """
    Handles AI consultation dialogue:
    Takes message, runs clinical red-flag check, runs AI service triage & follow-up,
    extracts structured symptoms, and retrieves verified medical sources.
    """
    user = get_current_user()
    patient_id = user['id'] if user else 18
    data = request.get_json() or {}
    message_content = (data.get('message_content') or data.get('content') or '').strip()

    if not message_content:
        return jsonify({'ok': False, 'error': 'Message content is required'}), 400

    # 1. Save user message to database
    try:
        database.execute(
            g.db,
            "INSERT INTO messages (assessment_id, role, content) VALUES (?, 'user', ?)",
            (consultation_id, message_content)
        )
    except Exception:
        pass

    # 2. Get past messages
    try:
        past_messages = database.fetch_all(
            g.db,
            "SELECT role, content FROM messages WHERE assessment_id = ? ORDER BY id ASC",
            (consultation_id,)
        ) or []
    except Exception:
        past_messages = [{'role': 'user', 'content': message_content}]

    # 3. Detect category and clinical red flags
    from backend.services.ai_service import detect_category, process_message, extract_structured_data_demo
    from backend.services.risk_engine import check_red_flags
    from ai.medical_retrieval.sources import retrieve_guidance

    category = detect_category(message_content)
    red_flags = check_red_flags(message_content)
    guidance_data = retrieve_guidance(message_content)

    if red_flags:
        is_urgent = True
        first_flag = red_flags[0]
        flag_reason = first_flag.get('name', 'Critical emergency symptoms')
        flag_action = first_flag.get('action', 'Seek immediate emergency medical care')
        reply_text = f"EMERGENCY WARNING: {flag_reason}. {flag_action}. Please seek immediate emergency medical care (Call 112 or 108) or go to the nearest emergency room immediately."
        reported_symptoms = [message_content]
        possible_causes = ["Acute Clinical Emergency", "Immediate Medical Evaluation Required"]
        general_guidance = "DO NOT DELAY. Call emergency services (112 / 108) immediately or visit the nearest emergency facility."
    else:
        is_urgent = False
        reply_data = process_message(past_messages, category)
        reply_text = reply_data.get('reply') or reply_data.get('question') or "I understand. Could you please describe when the symptoms started and if they are worsening?"
        
        structured = extract_structured_data_demo(past_messages, category)
        reported_symptoms = structured.get('main_symptoms') or [message_content]
        possible_causes = guidance_data.get('possible_causes', ["General physiological response", "Tension or fatigue"])
        general_guidance = guidance_data.get('guidance', "Rest adequately, hydrate, and monitor your symptoms.")

    # 4. Save assistant reply to database
    try:
        database.execute(
            g.db,
            "INSERT INTO messages (assessment_id, role, content) VALUES (?, 'assistant', ?)",
            (consultation_id, reply_text)
        )
    except Exception:
        pass

    sources = guidance_data.get('sources', [
        {"name": "NHS Health A-Z", "url": "https://www.nhs.uk/conditions/"},
        {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/"}
    ])

    return jsonify({
        'ok': True,
        'consultation_id': consultation_id,
        'assistant_reply': reply_text,
        'is_urgent_warning': is_urgent,
        'reported_symptoms': reported_symptoms,
        'possible_causes': possible_causes,
        'general_guidance': general_guidance,
        'medical_sources': sources
    })
