"""
End-to-end integration test suite verifying the combination of
clinic frontend with bestproject backend.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app

def run_tests():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()

    print("=" * 60)
    print("RUNNING END-TO-END INTEGRATION TESTS")
    print("=" * 60)

    # 1. Test Static Landing Page
    res = client.get('/')
    assert res.status_code == 200, f"Expected 200 on /, got {res.status_code}"
    assert b"AI Health Clinic" in res.data, "Missing brand title in landing page"
    print("  [PASS] Landing page (index.html) served successfully")

    # 2. Test Static Asset Serving
    res = client.get('/static/css/styles.css')
    assert res.status_code == 200, f"Expected 200 on styles.css, got {res.status_code}"
    print("  [PASS] CSS styles served via /static/css/styles.css")

    # 3. Test Static HTML page
    res = client.get('/static/html/patient-dashboard.html')
    assert res.status_code == 200, f"Expected 200 on patient-dashboard.html, got {res.status_code}"
    print("  [PASS] Portal pages served via /static/html/*.html")

    # 4. Test Login API with clinic credentials (Patient, Doctor, Admin)
    for email, pwd, role in [
        ('patient@clinic.com', 'Password@123', 'patient'),
        ('doctor@clinic.com', 'Password@123', 'doctor'),
        ('admin@clinic.com', 'Password@123', 'admin'),
        ('patient@demo.com', 'Patient@123', 'patient'),
        ('doctor@demo.com', 'Doctor@123', 'doctor'),
        ('admin@demo.com', 'Admin@123', 'admin'),
    ]:
        res = client.post('/api/auth/login', json={'email': email, 'password': pwd})
        assert res.status_code == 200, f"Expected 200 on login for {email}, got {res.status_code}: {res.data}"
        data = res.get_json()
        assert 'access_token' in data, f"Missing access_token for {email}"
        assert data['role'] == role, f"Role mismatch for {email}"

    # Retain patient token for patient tests
    res = client.post('/api/auth/login', json={'email': 'patient@clinic.com', 'password': 'Password@123'})
    data = res.get_json()
    token = data['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print(f"  [PASS] All patient, doctor, and admin accounts authenticated successfully")

    # 5. Test Patient Dashboard Summary API
    res = client.get('/api/patients/dashboard-summary', headers=headers)
    assert res.status_code == 200, f"Expected 200 on dashboard summary, got {res.status_code}: {res.data}"
    dash_data = res.get_json()
    assert 'user_name' in dash_data, "Missing user_name in summary"
    print(f"  [PASS] Patient dashboard summary: {dash_data['user_name']} has {dash_data['total_reports']} reports")

    # 6. Test AI Consultation Session Creation
    res = client.post('/api/consultations', json={'session_title': 'Headache assessment'}, headers=headers)
    assert res.status_code == 201, f"Expected 201 on new consultation, got {res.status_code}: {res.data}"
    consult_data = res.get_json()
    cid = consult_data['consultation_id']
    print(f"  [PASS] Created AI Consultation Session #{cid}")

    # 7. Test AI Consultation Chat Dialogue (bestproject AI service integration)
    res = client.post(f'/api/consultations/{cid}/messages', json={
        'message_content': 'I have a mild headache since yesterday'
    }, headers=headers)
    assert res.status_code == 200, f"Expected 200 on message send, got {res.status_code}: {res.data}"
    msg_data = res.get_json()
    assert 'assistant_reply' in msg_data, "Missing assistant_reply"
    assert len(msg_data['medical_sources']) > 0, "Missing medical sources"
    print(f"  [PASS] AI Consultation reply received: '{msg_data['assistant_reply'][:60]}...'")
    print(f"         Sources: {[s['name'] for s in msg_data['medical_sources']]}")

    # 8. Test Clinical Emergency Red Flag Triage
    res = client.post(f'/api/consultations/{cid}/messages', json={
        'message_content': 'Crushing chest pain radiating down left arm with shortness of breath'
    }, headers=headers)
    assert res.status_code == 200
    emergency_data = res.get_json()
    assert emergency_data['is_urgent_warning'] == True, "Failed to flag cardiac emergency"
    print(f"  [PASS] Emergency Red-Flag detection verified (is_urgent_warning=True)")

    # 9. Test Medical Reports API
    res = client.get('/api/medical-reports', headers=headers)
    assert res.status_code == 200, f"Expected 200 on reports, got {res.status_code}"
    reps = res.get_json()
    assert len(reps) > 0, "No medical reports returned"
    first_rep_id = reps[0]['report_id']
    print(f"  [PASS] Medical reports list: retrieved {len(reps)} reports")

    # 10. Test Report Details with Extracted Measurements
    res = client.get(f'/api/medical-reports/{first_rep_id}', headers=headers)
    assert res.status_code == 200, f"Expected 200 on report detail, got {res.status_code}"
    rep_detail = res.get_json()
    assert 'ai_summary' in rep_detail
    print(f"  [PASS] Report #{first_rep_id} details & AI lab explanation verified")

    # 11. Test Unified Health Timeline
    res = client.get('/api/timeline', headers=headers)
    assert res.status_code == 200, f"Expected 200 on timeline, got {res.status_code}"
    timeline_events = res.get_json()
    assert len(timeline_events) > 0, "No timeline events returned"
    print(f"  [PASS] Health timeline retrieved {len(timeline_events)} historical events")

    # 12. Test Doctors Directory & Booking
    res = client.get('/api/doctors', headers=headers)
    assert res.status_code == 200, f"Expected 200 on doctors, got {res.status_code}"
    doctors = res.get_json()
    assert len(doctors) > 0, "No doctors returned"
    first_doc_id = doctors[0]['doctor_id']
    print(f"  [PASS] Doctors catalog retrieved {len(doctors)} verified practitioners")

    # Book appointment
    res = client.post('/api/appointments', json={
        'doctor_id': first_doc_id,
        'appointment_date': '2026-10-25',
        'appointment_time': '11:00 AM',
        'consultation_type': 'Online',
        'reason_for_visit': 'Follow-up consultation'
    }, headers=headers)
    assert res.status_code == 201, f"Expected 201 on appointment booking, got {res.status_code}"
    print(f"  [PASS] Booked appointment with Doctor #{first_doc_id}")

    # 13. Test Pharmacy Search across destinations
    res = client.get('/api/pharmacies/search?query=Paracetamol', headers=headers)
    assert res.status_code == 200, f"Expected 200 on pharmacy search, got {res.status_code}"
    pharm_data = res.get_json()
    assert len(pharm_data['destinations']) >= 5, "Destinations incomplete"
    print(f"  [PASS] Pharmacy search: {len(pharm_data['destinations'])} destination links generated")

    # 14. Test Drug Allergy Safety Check
    res = client.post('/api/medicines/allergy-check?medicine_name=Amoxicillin', headers=headers)
    assert res.status_code == 200, f"Expected 200 on allergy check, got {res.status_code}"
    allergy_res = res.get_json()
    assert allergy_res['has_allergy_warning'] == True, "Failed to catch penicillin cross-sensitivity"
    print(f"  [PASS] Drug allergy cross-sensitivity check triggered successfully")

    # 15. Test Medicine Reminders
    res = client.get('/api/medicines/reminders', headers=headers)
    assert res.status_code == 200
    reminders = res.get_json()
    print(f"  [PASS] Medicine reminders retrieved ({len(reminders)} active)")

    print("=" * 60)
    print("ALL 15 INTEGRATION TESTS PASSED 100%!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
