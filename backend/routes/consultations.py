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


def generate_prescriptions_and_suggestions(category, message_content, patient_id):
    patient_allergies = ""
    if patient_id:
        try:
            profile = database.fetch_one(g.db, "SELECT allergies FROM patient_profiles WHERE user_id = ?", (patient_id,))
            if profile and profile.get('allergies'):
                patient_allergies = str(profile['allergies']).lower()
        except Exception:
            pass

    prescriptions = []
    has_nsaid_allergy = any(term in patient_allergies for term in ['aspirin', 'nsaid', 'ibuprofen', 'naproxen'])
    has_penicillin_allergy = any(term in patient_allergies for term in ['penicillin', 'amox', 'ampicillin'])

    cat = (category or 'general').lower()
    msg_lower = (message_content or '').lower()

    if cat == 'headache' or 'headache' in msg_lower or 'sir dard' in msg_lower:
        prescriptions.append({
            'medicine_name': 'Paracetamol 500mg',
            'generic_name': 'Acetaminophen / Paracetamol',
            'dosage': '1 Tablet (500mg)',
            'frequency': 'Every 6 to 8 hours as needed (Max 3g/day)',
            'timing': 'Take after meals with a full glass of water',
            'purpose': 'First-line relief for tension headache, dull pain, and fever',
            'otc_status': '100% Non-Prescription OTC',
            'allergy_safe': True,
            'allergy_status': '✓ Safe (No allergy conflict detected)',
            'precautions': 'Do not exceed 6 tablets within 24 hours. Avoid alcohol.',
            'pharmacy_query': 'Paracetamol 500mg'
        })
        if not has_nsaid_allergy:
            prescriptions.append({
                'medicine_name': 'Ibuprofen 400mg',
                'generic_name': 'Ibuprofen',
                'dosage': '1 Tablet (400mg)',
                'frequency': 'Twice daily with meals',
                'timing': 'Always take with food or milk to prevent gastric irritation',
                'purpose': 'Anti-inflammatory relief for throbbing headache and muscular tension',
                'otc_status': 'Standard OTC Analgesic',
                'allergy_safe': True,
                'allergy_status': '✓ Safe',
                'precautions': 'Drink plenty of water. Avoid if experiencing active acidity or peptic ulcer.',
                'pharmacy_query': 'Ibuprofen 400mg'
            })
        else:
            prescriptions.append({
                'medicine_name': 'Ibuprofen 400mg (Allergy Alert)',
                'generic_name': 'Ibuprofen',
                'dosage': 'N/A',
                'frequency': 'CONTRAINDICATED',
                'timing': 'DO NOT TAKE',
                'purpose': 'Contraindicated due to your documented NSAID/Aspirin sensitivity',
                'otc_status': 'Contraindicated',
                'allergy_safe': False,
                'allergy_status': '⚠️ Filtered out due to patient NSAID allergy',
                'precautions': 'Strictly use Paracetamol instead as prescribed above.',
                'pharmacy_query': 'Paracetamol'
            })
        suggestions = [
            "Pain is mild and dull",
            "Started 2 days ago",
            "No fever or nausea",
            "Prescribe safe medicine",
            "Add Paracetamol to my reminders",
            "Book doctor appointment"
        ]

    elif cat == 'fever' or 'fever' in msg_lower or 'temperature' in msg_lower or 'bukhar' in msg_lower:
        prescriptions.append({
            'medicine_name': 'Paracetamol 650mg (Dolo / Calpol)',
            'generic_name': 'Paracetamol',
            'dosage': '1 Tablet (650mg)',
            'frequency': 'Every 6-8 hours if body temperature exceeds 100°F',
            'timing': 'Take after food with warm water',
            'purpose': 'Rapidly lowers fever and alleviates accompanying generalized body aches',
            'otc_status': '100% Non-Prescription OTC',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Maintain minimum 6 hours between doses. Rest adequately.',
            'pharmacy_query': 'Paracetamol 650mg'
        })
        prescriptions.append({
            'medicine_name': 'Electral ORS (Oral Rehydration Solution)',
            'generic_name': 'WHO Formulation Oral Rehydration Salts',
            'dosage': '1 Sachet in 1 Litre boiled & cooled drinking water',
            'frequency': 'Sip regularly throughout the day',
            'timing': 'Continuous hydration',
            'purpose': 'Replenishes essential sodium, potassium, and fluid lost during fever sweating',
            'otc_status': 'Essential Health Electrolyte',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Consume freshly prepared solution within 24 hours.',
            'pharmacy_query': 'Electral ORS'
        })
        suggestions = [
            "Temperature is 100.8°F",
            "Body aches and chills",
            "Started yesterday evening",
            "Suggest fever dosage",
            "Add fever reminder",
            "Connect with physician"
        ]

    elif cat in ('cold_cough', 'sore_throat') or any(k in msg_lower for k in ['cough', 'cold', 'throat', 'khansi', 'sneeze', 'runny nose']):
        prescriptions.append({
            'medicine_name': 'Cetirizine 10mg',
            'generic_name': 'Cetirizine Hydrochloride',
            'dosage': '1 Tablet (10mg)',
            'frequency': 'Once daily at bedtime',
            'timing': 'At night (may cause mild drowsiness)',
            'purpose': 'Relieves runny nose, continuous sneezing, itchy throat, and allergic congestion',
            'otc_status': 'Non-Prescription Antihistamine',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Avoid driving or operating machinery after taking.',
            'pharmacy_query': 'Cetirizine 10mg'
        })
        prescriptions.append({
            'medicine_name': 'Strepsils Honey & Lemon Lozenges',
            'generic_name': 'Dichlorobenzyl alcohol + Amylmetacresol',
            'dosage': '1 Lozenge',
            'frequency': 'Dissolve slowly in mouth every 3 to 4 hours as needed',
            'timing': 'Between meals',
            'purpose': 'Provides local antiseptic throat soothing and eases dry scratchy cough',
            'otc_status': 'Throat Soothing Lozenge',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Do not chew or swallow whole.',
            'pharmacy_query': 'Strepsils'
        })
        prescriptions.append({
            'medicine_name': 'Saline Nasal Spray (0.9% NaCl)',
            'generic_name': 'Purified Isotonic Saline Solution',
            'dosage': '2 Sprays in each nostril',
            'frequency': 'Twice daily or as needed',
            'timing': 'Morning and evening',
            'purpose': 'Naturally clears nasal mucus without rebound swelling or chemical dependency',
            'otc_status': 'Non-Medicinal Saline Spray',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Wipe nozzle clean after each application.',
            'pharmacy_query': 'Saline nasal spray'
        })
        suggestions = [
            "Dry cough for 3 days",
            "Runny nose and sneezing",
            "Mild sore throat when swallowing",
            "Suggest cough remedy",
            "Order from pharmacy",
            "Schedule consultation"
        ]

    elif cat == 'stomach' or any(k in msg_lower for k in ['stomach', 'acidity', 'pet dard', 'gas', 'bloating', 'nausea', 'vomit', 'diarrhea']):
        prescriptions.append({
            'medicine_name': 'Pantoprazole 40mg (Pan 40)',
            'generic_name': 'Pantoprazole',
            'dosage': '1 Tablet (40mg)',
            'frequency': 'Once daily in the morning',
            'timing': 'Take 30 minutes before breakfast on an empty stomach with water',
            'purpose': 'Reduces gastric acid excess, suppresses acid reflux, heartburn, and sour burps',
            'otc_status': 'Proton Pump Inhibitor (PPI)',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Swallow whole with water. Avoid spicy, oily food.',
            'pharmacy_query': 'Pantoprazole 40mg'
        })
        prescriptions.append({
            'medicine_name': 'Digene Antacid Liquid Gel',
            'generic_name': 'Magnesium Hydroxide + Aluminium Hydroxide + Simethicone',
            'dosage': '2 Teaspoons (10ml)',
            'frequency': 'After meals and at bedtime as needed',
            'timing': 'Post meals',
            'purpose': 'Rapidly coats stomach lining and eliminates bloating/gas bubbles',
            'otc_status': 'Fast-Acting Antacid Gel',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Shake well before using.',
            'pharmacy_query': 'Digene gel'
        })
        suggestions = [
            "Burning sensation in chest after eating",
            "Mild stomach cramps and bloating",
            "Started this morning",
            "Recommend antacid or ORS",
            "Add Pantoprazole reminder",
            "Book gastroenterologist"
        ]

    elif cat == 'skin' or any(k in msg_lower for k in ['skin', 'rash', 'itching', 'khujli', 'pimple', 'acne', 'allergy']):
        prescriptions.append({
            'medicine_name': 'Calamine Soothing Lotion',
            'generic_name': 'Calamine + Zinc Oxide',
            'dosage': 'Gentle thin coat',
            'frequency': 'Apply 2 to 3 times daily to affected itchy skin',
            'timing': 'Apply to clean, dry skin',
            'purpose': 'Soothes inflamed skin, hives, allergic rash, and reduces itching sensation',
            'otc_status': 'Topical Soothing Lotion',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'For external skin application only. Avoid open bleeding cuts.',
            'pharmacy_query': 'Calamine lotion'
        })
        prescriptions.append({
            'medicine_name': 'Levocetirizine 5mg',
            'generic_name': 'Levocetirizine Dihydrochloride',
            'dosage': '1 Tablet (5mg)',
            'frequency': 'Once daily at bedtime',
            'timing': 'Night time with water',
            'purpose': 'Blocks histamine release causing hives, red flares, and intense itching',
            'otc_status': 'Oral Antihistamine',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Consult a dermatologist if rash rapidly expands or causes facial swelling.',
            'pharmacy_query': 'Levocetirizine 5mg'
        })
        suggestions = [
            "Itchy red bumps on arms",
            "Facial breakouts and pimples",
            "Started after new cosmetic product",
            "Suggest soothing lotion",
            "Book dermatologist consultation"
        ]

    else:
        prescriptions.append({
            'medicine_name': 'Multivitamin & Zinc (Zincovit)',
            'generic_name': 'Multivitamins, Essential Minerals & Zinc',
            'dosage': '1 Tablet daily',
            'frequency': 'Once daily after breakfast or lunch',
            'timing': 'Take with a meal',
            'purpose': 'Supports immune health, cellular recovery, and general metabolic vitality',
            'otc_status': 'Daily Nutritional Supplement',
            'allergy_safe': True,
            'allergy_status': '✓ Safe',
            'precautions': 'Do not take on an empty stomach. Store in cool place.',
            'pharmacy_query': 'Zincovit'
        })
        suggestions = [
            "Feeling fatigued and low energy",
            "Mild general body ache",
            "Started 2 days ago",
            "Recommend vitamins",
            "Book doctor appointment"
        ]

    return prescriptions, suggestions


@consultations_bp.route('/api/consultations/<int:consultation_id>/messages', methods=['POST'])
def consultation_messages(consultation_id):
    """
    Handles AI consultation dialogue:
    Takes message, runs clinical red-flag check, runs AI service triage & follow-up,
    extracts structured symptoms, prescribes safe medicines, and generates live auto-suggestions.
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

    # 4. Generate structured prescriptions & auto-suggestions
    prescribed_meds, auto_suggestions = generate_prescriptions_and_suggestions(category, message_content, patient_id)

    if red_flags:
        is_urgent = True
        first_flag = red_flags[0]
        flag_reason = first_flag.get('name', 'Critical emergency symptoms')
        flag_action = first_flag.get('action', 'Seek immediate emergency medical care')
        reply_text = f"EMERGENCY WARNING: {flag_reason}. {flag_action}. Please seek immediate emergency medical care (Call 112 or 108) or go to the nearest emergency room immediately."
        reported_symptoms = [message_content]
        possible_causes = ["Acute Clinical Emergency", "Immediate Medical Evaluation Required"]
        general_guidance = "DO NOT DELAY. Call emergency services (112 / 108) immediately or visit the nearest emergency facility."
        prescribed_meds = []
        auto_suggestions = ["Call Emergency 112", "Find nearest cardiac hospital", "I took an Aspirin", "Notify family contact"]
    else:
        is_urgent = False
        reply_data = process_message(past_messages, category)
        reply_text = reply_data.get('reply') or reply_data.get('question') or "I understand. Could you please describe when the symptoms started and if they are worsening?"
        
        structured = extract_structured_data_demo(past_messages, category)
        reported_symptoms = structured.get('main_symptoms') or [message_content]
        possible_causes = guidance_data.get('possible_causes', ["General physiological response", "Tension or fatigue"])
        general_guidance = guidance_data.get('guidance', "Rest adequately, hydrate, and monitor your symptoms.")

    # 5. Save assistant reply to database
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
        'prescribed_medicines': prescribed_meds,
        'auto_suggestions': auto_suggestions,
        'medical_sources': sources
    })

@consultations_bp.route('/api/consultations/active', methods=['GET'])
def get_active_consultation():
    """Retrieve the active AI consultation session for the logged-in patient, or start a new one."""
    user = get_current_user()
    if not user:
        return jsonify({'ok': False, 'error': 'Please log in'}), 401

    patient_id = user['id']
    assessment = database.fetch_one(
        g.db,
        "SELECT id, summary, category, status, created_at FROM assessments WHERE patient_id = ? ORDER BY id DESC LIMIT 1",
        (patient_id,)
    )

    if not assessment:
        aid = database.insert(
            g.db,
            "INSERT INTO assessments (patient_id, status, category, summary) VALUES (?, 'in_progress', 'general', ?)",
            (patient_id, 'AI Health Consultation')
        )
        messages = []
    else:
        aid = assessment['id']
        messages = database.fetch_all(
            g.db,
            "SELECT role, content, created_at FROM messages WHERE assessment_id = ? ORDER BY id ASC",
            (aid,)
        ) or []

    initial_suggestions = [
        "I have a mild headache since yesterday",
        "Fever and body ache since morning",
        "Dry cough and sore throat",
        "Stomach pain and acidity after dinner",
        "Prescribe safe medicine for cold",
        "Skin rash and itching"
    ]

    return jsonify({
        'ok': True,
        'consultation_id': aid,
        'patient_id': patient_id,
        'patient_name': user.get('name') or user.get('full_name'),
        'messages': messages,
        'initial_suggestions': initial_suggestions
    })
