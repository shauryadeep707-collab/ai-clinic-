"""
Patient routes for AI Health Clinic & Assistant.
Provides dashboard summaries, profile access, and health metric tracking.
"""

from flask import Blueprint, request, jsonify, g
from backend.auth_utils import role_required, get_current_user
from backend import db as database

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/api/patients/dashboard-summary', methods=['GET'])
def get_dashboard_summary():
    """Returns patient statistics and upcoming activity for the portal dashboard."""
    user = get_current_user()
    if not user:
        return jsonify({
            'user_name': 'Rohan Sharma',
            'patient_id': 1,
            'total_reports': 5,
            'upcoming_appointments': 1,
            'active_prescriptions': 2,
            'recent_reports': [
                {'report_id': 1, 'title': 'Blood Test Report', 'date': '15 Oct 2024', 'icon': 'fa-droplet'},
                {'report_id': 2, 'title': 'X-Ray (Chest)', 'date': '28 Sep 2024', 'icon': 'fa-x-ray'},
                {'report_id': 3, 'title': 'MRI Report', 'date': '12 Aug 2024', 'icon': 'fa-brain'}
            ]
        })

    user_id = user['id']
    user_name = user.get('name') or user.get('full_name') or 'Patient'

    # Count reports
    try:
        rep_row = database.fetch_one(g.db, "SELECT COUNT(*) as c FROM medical_reports WHERE patient_user_id = ?", (user_id,))
        total_reports = rep_row['c'] if rep_row else 0
    except Exception:
        total_reports = 0

    # Count upcoming appointments
    try:
        appt_row = database.fetch_one(g.db, "SELECT COUNT(*) as c FROM appointments WHERE patient_user_id = ? AND status = 'Confirmed'", (user_id,))
        upcoming_appointments = appt_row['c'] if appt_row else 0
    except Exception:
        upcoming_appointments = 0

    # Active reminders / prescriptions
    try:
        rem_row = database.fetch_one(g.db, "SELECT COUNT(*) as c FROM medicine_reminders WHERE patient_user_id = ? AND is_active = 1", (user_id,))
        active_prescriptions = rem_row['c'] if rem_row else 0
    except Exception:
        active_prescriptions = 0

    # Recent reports
    recent_reports = []
    try:
        reps = database.fetch_all(g.db, "SELECT id as report_id, report_title as title, test_date as date, report_category as category FROM medical_reports WHERE patient_user_id = ? ORDER BY id DESC LIMIT 4", (user_id,))
        for r in reps:
            cat = (r.get('category') or '').lower()
            icon = 'fa-droplet' if 'blood' in cat else ('fa-x-ray' if 'imaging' in cat or 'x-ray' in cat else 'fa-file-medical')
            recent_reports.append({
                'report_id': r['report_id'],
                'title': r['title'],
                'date': str(r['date']),
                'icon': icon
            })
    except Exception:
        pass

    return jsonify({
        'user_name': user_name,
        'patient_id': user_id,
        'email': user['email'],
        'total_reports': total_reports,
        'upcoming_appointments': upcoming_appointments,
        'active_prescriptions': active_prescriptions,
        'recent_reports': recent_reports
    })

@patients_bp.route('/api/patients/profile', methods=['GET', 'PUT'])
def patient_profile():
    """Get or update patient profile."""
    user = get_current_user()
    if not user:
        return jsonify({'ok': False, 'error': 'Please log in', 'detail': 'Unauthorized'}), 401

    user_id = user['id']

    if request.method == 'GET':
        profile = database.fetch_one(g.db, "SELECT * FROM patient_profiles WHERE user_id = ?", (user_id,)) or {}
        return jsonify({
            'ok': True,
            'user_id': user_id,
            'full_name': user['name'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'age': profile.get('age'),
            'gender': profile.get('gender'),
            'chronic_conditions': profile.get('chronic_conditions', ''),
            'allergies': profile.get('allergies', '')
        })

    # PUT update
    data = request.get_json() or {}
    full_name = data.get('full_name') or data.get('name')
    phone = data.get('phone')
    age = data.get('age')
    gender = data.get('gender')
    chronic_conditions = data.get('chronic_conditions')
    allergies = data.get('allergies')

    if full_name or phone:
        sql = "UPDATE users SET "
        params = []
        updates = []
        if full_name:
            updates.append("name = ?")
            params.append(full_name)
        if phone:
            updates.append("phone = ?")
            params.append(phone)
        sql += ", ".join(updates) + " WHERE id = ?"
        params.append(user_id)
        database.execute(g.db, sql, tuple(params))

    existing_profile = database.fetch_one(g.db, "SELECT user_id FROM patient_profiles WHERE user_id = ?", (user_id,))
    if existing_profile:
        database.execute(
            g.db,
            "UPDATE patient_profiles SET age = COALESCE(?, age), gender = COALESCE(?, gender), chronic_conditions = COALESCE(?, chronic_conditions), allergies = COALESCE(?, allergies) WHERE user_id = ?",
            (age, gender, chronic_conditions, allergies, user_id)
        )
    else:
        database.execute(
            g.db,
            "INSERT INTO patient_profiles (user_id, age, gender, chronic_conditions, allergies) VALUES (?, ?, ?, ?, ?)",
            (user_id, age, gender, chronic_conditions, allergies)
        )

    return jsonify({
        'ok': True,
        'message': 'Profile updated successfully',
        'full_name': full_name or user['name'],
        'email': user['email']
    })
