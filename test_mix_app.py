"""
End-to-end integration test suite verifying the combination of
clinic frontend with bestproject backend.
"""

import sys
import os
import json
import secrets
import uuid

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

    # 16. Test Doctor Registration Flow (is_verified initially 0)
    import uuid
    unique_suffix = uuid.uuid4().hex[:6]
    doc_email = f"dr.rajesh.{unique_suffix}@clinic.com"
    doc_reg_res = client.post('/api/auth/register', json={
        'name': f'Dr. Rajesh Kumar {unique_suffix.upper()}',
        'email': doc_email,
        'password': 'Password@123',
        'role': 'doctor',
        'phone': '+91 98765 43210',
        'specialization': 'Cardiologist',
        'medical_degree': 'MBBS, MD (Cardiology)',
        'registration_number': f'MCI-{secrets.randbelow(89999)+10000}',
        'medical_council': 'Delhi Medical Council',
        'experience_years': 12,
        'fee': 1000.0,
        'medical_college': 'AIIMS New Delhi',
        'graduation_year': 2012,
        'clinic_name': 'Heart Care & Vascular Clinic',
        'address': '104 Ring Road',
        'city': 'New Delhi'
    })
    assert doc_reg_res.status_code == 201 or doc_reg_res.status_code == 200, f"Doctor registration failed: {doc_reg_res.data}"
    reg_data = doc_reg_res.get_json()
    doc_token = reg_data['access_token']
    doc_headers = {'Authorization': f'Bearer {doc_token}'}
    assert reg_data.get('is_verified') == 0 or reg_data.get('data', {}).get('is_verified') == 0, "New doctor should have is_verified=0 before DigiLocker check"
    print(f"  [PASS] Doctor registered with pending verification (is_verified=0)")

    # 17. Test DigiLocker & NAD Credential Verification
    verify_res = client.post('/api/doctors/digilocker-verify', json={
        'medical_degree': 'MBBS, MD (Cardiology)',
        'medical_college': 'AIIMS New Delhi',
        'graduation_year': 2012,
        'medical_reg_number': f'MCI-{secrets.randbelow(89999)+10000}',
        'registration_council': 'Delhi Medical Council',
        'specialization': 'Cardiologist',
        'experience_years': 12,
        'consultation_fee': 1000.0,
        'clinic_name': 'Heart Care & Vascular Clinic',
        'aadhaar_last_four': '9142'
    }, headers=doc_headers)
    assert verify_res.status_code == 200, f"DigiLocker verification failed: {verify_res.data}"
    verify_data = verify_res.get_json()
    assert verify_data['ok'] is True
    assert verify_data['is_verified'] == 1
    assert verify_data['digilocker_verified'] == 1
    assert 'nad_certificate_id' in verify_data
    assert verify_data['nad_certificate_id'].startswith('NAD-NMC-')
    print(f"  [PASS] DigiLocker verification approved: Certificate {verify_data['nad_certificate_id']} issued, is_verified=1")

    # 18. Test Doctor Verification Status Endpoint
    status_res = client.get('/api/doctors/verification-status', headers=doc_headers)
    assert status_res.status_code == 200
    stat = status_res.get_json()
    assert stat['is_verified'] == 1
    assert stat['digilocker_verified'] == 1
    assert stat['nad_certificate_id'] == verify_data['nad_certificate_id']
    print(f"  [PASS] Doctor verification status API verified active NAD accreditation")

    # 19. Test New Patient Data Privacy & Inserting Own Reports
    new_pat_suffix = uuid.uuid4().hex[:6]
    pat_email = f"patient.ananya.{new_pat_suffix}@clinic.com"
    pat_reg_res = client.post('/api/auth/register', json={
        'name': f'Ananya Roy {new_pat_suffix.upper()}',
        'email': pat_email,
        'password': 'Password@123',
        'role': 'patient',
        'phone': '+91 99887 76655',
        'allergies': 'Penicillin, Aspirin'
    })
    assert pat_reg_res.status_code == 200 or pat_reg_res.status_code == 201
    pat_data = pat_reg_res.get_json()
    new_pat_token = pat_data['access_token']
    new_pat_headers = {'Authorization': f'Bearer {new_pat_token}'}

    # Verify new patient sees ONLY their own reports (0 initially, NOT Rohan Sharma's reports)
    initial_reps = client.get('/api/medical-reports', headers=new_pat_headers).get_json()
    assert len(initial_reps) == 0, f"New patient should have 0 reports initially, got {len(initial_reps)}"
    print(f"  [PASS] New patient data isolation verified: starts with 0 reports (isolated from other patients)")

    # Patient inserts their own report via direct lab text input
    upload_res = client.post('/api/medical-reports/upload', data={
        'report_title': 'Ananya Lipid & Glucose Profile',
        'report_category': 'Blood Tests',
        'test_date': '2026-10-21',
        'issuing_lab': 'Apollo Diagnostics',
        'custom_raw_text': 'Total Cholesterol: 185 mg/dL. Fasting Blood Sugar: 92 mg/dL. HDL: 55 mg/dL. Triglycerides: 140 mg/dL.'
    }, headers=new_pat_headers)
    assert upload_res.status_code == 201, f"Report upload failed: {upload_res.data}"
    up_data = upload_res.get_json()
    assert up_data['ok'] is True
    ananya_rep_id = up_data['report_id']
    print(f"  [PASS] Patient successfully inserted own report #{ananya_rep_id} with direct lab text entry")

    # Verify report is now in Ananya's list
    ananya_reps = client.get('/api/medical-reports', headers=new_pat_headers).get_json()
    assert len(ananya_reps) == 1
    assert ananya_reps[0]['report_title'] == 'Ananya Lipid & Glucose Profile'

    # Verify Rohan / clinic demo patient does NOT see Ananya's report
    rohan_reps = client.get('/api/medical-reports', headers=headers).get_json()
    assert not any(r['id'] == ananya_rep_id for r in rohan_reps), "Data privacy breach: Demo patient can see Ananya's report!"
    print(f"  [PASS] Patient cross-contamination privacy confirmed: other patients cannot access this report")

    # 20. Test AI Consultation with Prescribed Medicine & Auto-Suggestions
    # Get or create active consultation session
    active_chat_res = client.get('/api/consultations/active', headers=new_pat_headers)
    assert active_chat_res.status_code == 200
    active_chat = active_chat_res.get_json()
    cid = active_chat['consultation_id']
    assert len(active_chat['initial_suggestions']) > 0
    print(f"  [PASS] Active AI consultation session initialized #{cid} with {len(active_chat['initial_suggestions'])} auto-suggestions")

    # Send symptom message: headache
    chat_res = client.post(f'/api/consultations/{cid}/messages', json={
        'message_content': 'I have a throbbing headache since yesterday'
    }, headers=new_pat_headers)
    assert chat_res.status_code == 200
    cdata = chat_res.get_json()
    assert 'prescribed_medicines' in cdata, "Missing prescribed_medicines in AI response"
    assert len(cdata['prescribed_medicines']) > 0, "No medicines prescribed by AI for headache"
    assert 'auto_suggestions' in cdata, "Missing auto_suggestions in AI response"
    assert len(cdata['auto_suggestions']) > 0, "No auto-suggestions provided"

    # Verify prescribed medicine details & allergy safety check (Ananya is allergic to Aspirin/NSAID)
    med1 = cdata['prescribed_medicines'][0]
    assert 'Paracetamol' in med1['medicine_name']
    assert med1['allergy_safe'] is True
    assert 'dosage' in med1

    # Check that Ibuprofen was flagged with allergy warning for Ananya
    nsaid_med = [m for m in cdata['prescribed_medicines'] if 'Ibuprofen' in m['medicine_name']]
    if nsaid_med:
        assert nsaid_med[0]['allergy_safe'] is False, "Aspirin/NSAID allergy failed to flag on Ibuprofen!"
        print(f"  [PASS] AI Allergy check passed: Flagged Ibuprofen for patient with documented NSAID allergy")

    print(f"  [PASS] AI prescribed {med1['medicine_name']} ({med1['dosage']}) with {len(cdata['auto_suggestions'])} live suggestion chips")

    # Patient adds the prescribed medicine to reminders
    rem_add_res = client.post('/api/medicines/reminders', json={
        'medicine_name': med1['medicine_name'],
        'dosage': med1['dosage'],
        'reminder_time': '09:00',
        'days_of_week': 'Daily'
    }, headers=new_pat_headers)
    assert rem_add_res.status_code == 201
    print(f"  [PASS] Prescribed medicine successfully saved to patient medicine reminders")

    print("=" * 60)
    print("ALL 20 INTEGRATION TESTS PASSED 100%!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
