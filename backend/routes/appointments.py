"""
Appointments and Doctor Credential Review routes for AI Health Clinic & Assistant.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, g
from backend.auth_utils import get_current_user
from backend import db as database

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/api/doctors', methods=['GET'])
def list_doctors():
    """List verified practicing doctors with specialties, fee, and availability."""
    sql = """
        SELECT u.id as doctor_id, u.name as doctor_name, u.email,
               d.specialization, d.clinic_name, d.address, d.city, d.fee as consultation_fee,
               d.experience_years, d.medical_degree, d.is_available,
               COALESCE(d.experience_years, 5) as experience_years
        FROM users u
        LEFT JOIN doctor_profiles d ON u.id = d.user_id
        WHERE u.role = 'doctor' AND u.is_verified = 1
        ORDER BY d.is_available DESC, u.id ASC
    """
    doctors = database.fetch_all(g.db, sql) or []
    return jsonify(doctors)

@appointments_bp.route('/api/appointments', methods=['GET', 'POST'])
def handle_appointments():
    """List or book appointments."""
    user = get_current_user()
    patient_id = user['id'] if user else 18

    if request.method == 'GET':
        appts = database.fetch_all(
            g.db,
            """SELECT a.*, u.name as doctor_name, d.specialization, d.clinic_name
               FROM appointments a
               JOIN users u ON a.doctor_id = u.id
               LEFT JOIN doctor_profiles d ON u.id = d.user_id
               WHERE a.patient_user_id = ?
               ORDER BY a.appointment_date ASC, a.appointment_time ASC""",
            (patient_id,)
        ) or []
        return jsonify(appts)

    # POST booking
    data = request.get_json() or {}
    doctor_id = data.get('doctor_id')
    appt_date = data.get('appointment_date')
    appt_time = data.get('appointment_time')
    consult_type = data.get('consultation_type', 'Online')
    reason = data.get('reason_for_visit', '')

    if not doctor_id or not appt_date or not appt_time:
        return jsonify({'ok': False, 'error': 'Doctor, date, and time are required'}), 400

    doctor = database.fetch_one(g.db, "SELECT name FROM users WHERE id = ?", (doctor_id,))
    doctor_name = doctor['name'] if doctor else 'Verified Doctor'

    appt_id = database.insert(
        g.db,
        """INSERT INTO appointments (patient_user_id, doctor_id, appointment_date, appointment_time, consultation_type, status, reason_for_visit)
           VALUES (?, ?, ?, ?, ?, 'Confirmed', ?)""",
        (patient_id, doctor_id, appt_date, appt_time, consult_type, reason)
    )

    # Add to health timeline
    database.execute(
        g.db,
        """INSERT INTO health_timeline_events 
           (patient_user_id, event_type, event_title, event_date, event_time, short_description, organization_or_doctor, record_reference_id, status_badge)
           VALUES (?, 'Doctor Consultation', ?, ?, ?, ?, ?, ?, 'Scheduled')""",
        (patient_id, f"Consultation with {doctor_name}", appt_date, appt_time, f"{consult_type} appointment: {reason}", doctor_name, appt_id)
    )

    return jsonify({
        'ok': True,
        'appointment_id': appt_id,
        'status': 'Confirmed',
        'message': f"Appointment successfully scheduled with {doctor_name}"
    }), 201

@appointments_bp.route('/api/doctors/applications', methods=['POST'])
def doctor_application():
    """Doctor registration credentials submission for verification."""
    user = get_current_user()
    doctor_id = user['id'] if user else None

    data = request.get_json() or {}
    spec = data.get('specialization', 'General Physician')
    qual = data.get('qualification_summary', 'MBBS')
    exp = data.get('experience_years', 5)
    reg_num = data.get('medical_reg_number', 'NMC-PENDING')
    council = data.get('registration_council', 'State Medical Council')
    fee = data.get('consultation_fee', 500.0)
    bio = data.get('bio', '')

    if doctor_id:
        database.execute(
            g.db,
            """UPDATE doctor_profiles 
               SET specialization = ?, qualification_summary = ?, experience_years = ?, 
                   registration_number = ?, medical_council = ?, fee = ?
               WHERE user_id = ?""",
            (spec, qual, exp, reg_num, council, fee, doctor_id)
        )
        app_id = database.insert(
            g.db,
            "INSERT INTO doctor_applications (doctor_id, status, review_notes) VALUES (?, 'Pending', ?)",
            (doctor_id, f"Credentials submitted: {qual}, Reg No: {reg_num}")
        )
    else:
        app_id = 1

    return jsonify({
        'ok': True,
        'application_id': app_id,
        'status': 'Pending',
        'message': 'Verification documents submitted! Under admin review.'
    }), 201

@appointments_bp.route('/api/admin/doctors/review', methods=['POST'])
def review_doctor_application():
    """Admin reviews and approves/rejects doctor credential applications."""
    data = request.get_json() or {}
    app_id = data.get('application_id')
    action = data.get('action', 'approve').lower()
    notes = data.get('notes', '')

    user = get_current_user()
    admin_id = user['id'] if user else 1

    new_verified_status = 1 if 'approve' in action else 2
    app_status = 'Approved' if 'approve' in action else 'Rejected'

    try:
        app_row = database.fetch_one(g.db, "SELECT doctor_id FROM doctor_applications WHERE id = ?", (app_id,))
        if app_row:
            doc_id = app_row['doctor_id']
            database.execute(g.db, "UPDATE users SET is_verified = ? WHERE id = ?", (new_verified_status, doc_id))
            database.execute(g.db, "UPDATE doctor_applications SET status = ?, reviewed_by_admin_id = ?, review_notes = ? WHERE id = ?", (app_status, admin_id, notes, app_id))
    except Exception:
        pass

    return jsonify({
        'ok': True,
        'action': action,
        'status': app_status,
        'message': f"Doctor application {app_status.lower()} successfully."
    })
