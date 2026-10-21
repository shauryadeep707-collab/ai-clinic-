"""
Unified Health Timeline routes for AI Health Clinic & Assistant.
Chronologically aggregates medical history, reports, doctor visits, and AI triage sessions.
"""

from flask import Blueprint, request, jsonify, g
from backend.auth_utils import get_current_user
from backend import db as database

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/api/timeline', methods=['GET'])
def get_timeline():
    """Retrieve filtered health timeline events strictly for the active patient."""
    user = get_current_user()
    if not user:
        # Fallback to default patient for demo visits
        user = database.fetch_one(g.db, "SELECT id, name, email, role FROM users WHERE role = 'patient' ORDER BY id ASC LIMIT 1")
    if not user:
        return jsonify([])

    role = user.get('role', 'patient')
    req_patient_id = request.args.get('patient_id')
    if req_patient_id and role in ('admin', 'doctor'):
        patient_id = int(req_patient_id)
    else:
        patient_id = user['id']

    event_type = request.args.get('event_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    sql = "SELECT * FROM health_timeline_events WHERE patient_user_id = ?"
    params = [patient_id]

    if event_type and event_type != 'all':
        sql += " AND event_type = ?"
        params.append(event_type)
    if date_from:
        sql += " AND event_date >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND event_date <= ?"
        params.append(date_to)

    sql += " ORDER BY event_date DESC, id DESC"

    events = database.fetch_all(g.db, sql, tuple(params)) or []

    # Map id -> event_id for frontend compatibility
    results = []
    for ev in events:
        d = dict(ev)
        d['event_id'] = d.get('id')
        d['event_date'] = str(d.get('event_date'))
        results.append(d)

    return jsonify(results)
