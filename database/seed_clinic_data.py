"""
Seed clinic demo users, pharmacy providers, reports, and timeline events
into the active database (Postgres and SQLite).
"""
import sys
import os
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import config
from backend import db as database

def seed():
    conn = database.get_connection()
    db_type = config.DB_TYPE
    print(f"Seeding demo data for db_type={db_type}...")

    # 1. Ensure clinic accounts exist
    clinic_users = [
        ('Rohan Sharma', 'patient@clinic.com', 'Password@123', 'patient', '+91 98765 43210', 1),
        ('Dr. Amit Verma', 'doctor@clinic.com', 'Password@123', 'doctor', '+91 98765 43211', 1),
        ('Dr. Priya Mehta', 'dr.priya@clinic.com', 'Password@123', 'doctor', '+91 98765 43212', 1),
        ('System Administrator', 'admin@clinic.com', 'Password@123', 'admin', '+91 98765 43213', 1),
    ]

    for name, email, pwd, role, phone, is_verified in clinic_users:
        existing = database.fetch_one(conn, "SELECT id FROM users WHERE email = ?", (email,))
        if not existing:
            pwd_hash = generate_password_hash(pwd)
            u_id = database.insert(
                conn,
                "INSERT INTO users (name, email, password_hash, role, phone, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
                (name, email, pwd_hash, role, phone, is_verified)
            )
            if role == 'patient':
                database.execute(
                    conn,
                    "INSERT INTO patient_profiles (user_id, age, gender, chronic_conditions, allergies) VALUES (?, ?, ?, ?, ?)",
                    (u_id, 28, 'Male', 'Mild Asthma', 'Penicillin')
                )
            elif role == 'doctor':
                spec = 'Cardiologist' if 'Priya' in name else 'General Physician'
                clinic_name = 'Apollo Heart Center' if 'Priya' in name else 'Dr. Amit Verma Clinic'
                database.execute(
                    conn,
                    """INSERT INTO doctor_profiles 
                       (user_id, specialization, clinic_name, address, city, lat, lng, fee, experience_years,
                        medical_degree, registration_number, medical_council, graduation_year, medical_college, is_available)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                    (u_id, spec, clinic_name, 'Rajpur Road', 'Dehradun', 30.3165, 78.0322, 500.0, 10,
                     'MBBS, MD', f'NMC-{u_id}982', 'Uttarakhand Medical Council', 2014, 'AIIMS New Delhi')
                )
            print(f"Created user {email} (id: {u_id})")

    # Get patient user ID for Rohan Sharma or Rahul Sharma
    pat = database.fetch_one(conn, "SELECT id FROM users WHERE email = 'patient@clinic.com'")
    patient_id = pat['id'] if pat else 2

    # 2. Pharmacy Providers
    pharmacies = [
        ('Apollo Pharmacy', 'https://www.apollopharmacy.in/', 'https://www.apollopharmacy.in/search-medicines/{query}', 'Retail & Online Pharmacy', 'https://assets.apollo247.com/images/apollo_logo.svg'),
        ('Tata 1mg', 'https://www.1mg.com/', 'https://www.1mg.com/search/all?name={query}', 'Online Pharmacy', 'https://res.cloudinary.com/du8msdgbj/image/upload/v1580982542/quick_buy_reorder_1mg.png'),
        ('Netmeds', 'https://www.netmeds.com/c/', 'https://www.netmeds.com/catalogsearch/result?q={query}', 'Online Pharmacy', 'https://www.netmeds.com/assets/gloryweb/images/home-logo-netmeds-new.svg'),
        ('PharmEasy', 'https://pharmeasy.in/online-medicine-order', 'https://pharmeasy.in/search/all?name={query}', 'Online Pharmacy', 'https://assets.pharmeasy.in/apothecary/images/logo_big.svg'),
        ('Swiggy Instamart', 'https://www.swiggy.com/instamart', 'https://www.swiggy.com/instamart/search?custom_back=true&query={query}', 'Quick Delivery', 'https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,w_288,h_288/instamart_logo'),
        ('Blinkit Medicines', 'https://blinkit.com/cn/medicines/cid/287/7275', 'https://blinkit.com/s/?q={query}', 'Quick Delivery', 'https://blinkit.com/images/header/blinkit-logo.svg'),
        ('Amazon Pharmacy', 'https://www.amazon.in/pharmacy', 'https://www.amazon.in/s?k={query}&i=hpc', 'Online Pharmacy', 'https://m.media-amazon.com/images/G/31/AmazonPharmacy/Amazon_Pharmacy_Logo.png'),
    ]

    for name, base_url, tpl, tag, logo in pharmacies:
        ex = database.fetch_one(conn, "SELECT id FROM pharmacy_providers WHERE provider_name = ?", (name,))
        if not ex:
            database.execute(
                conn,
                "INSERT INTO pharmacy_providers (provider_name, base_url, search_url_template, category_tag, is_active, logo_url) VALUES (?, ?, ?, ?, 1, ?)",
                (name, base_url, tpl, tag, logo)
            )

    # 3. Medical Reports
    rep_count = database.fetch_one(conn, "SELECT COUNT(*) as c FROM medical_reports WHERE patient_user_id = ?", (patient_id,))
    if rep_count['c'] == 0:
        reports = [
            (patient_id, 'Blood Test Report', 'Blood Tests', 'Complete Blood Count (CBC) & Vitamin Panel', '2024-10-15', 'Max Diagnostic Laboratory', 'cbc_report_oct2024.pdf', 'backend/uploads/reports/sample_cbc.pdf', 345120, 'Hemoglobin: 14.2 g/dL. Total WBC: 7,200 /uL. Platelets: 240,000 /uL. Fasting Blood Sugar: 94 mg/dL. Serum Vitamin D (25-OH): 18.2 ng/mL (Deficient). Creatinine: 0.9 mg/dL.', 'CBC parameters within normal range. Mild Vitamin D insufficiency observed.'),
            (patient_id, 'Chest X-Ray', 'Imaging', 'PA View Chest Radiograph', '2024-09-28', 'Apollo Imaging Center', 'chest_xray_sep2024.jpg', 'backend/uploads/reports/sample_xray.jpg', 1250440, 'Bilateral lung fields clear. Normal cardiothoracic ratio. Sharp angles. No active lesion.', 'Clear chest radiograph. No evidence of infection or cardiomegaly.'),
            (patient_id, 'Brain MRI Report', 'Imaging', 'Brain MRI Screening', '2024-08-12', 'Medanta Diagnostic Center', 'brain_mri_aug2024.pdf', 'backend/uploads/reports/sample_mri.pdf', 840210, 'Normal brain parenchyma. No intracranial hemorrhage or acute infarct detected.', 'Normal brain MRI screening report.'),
            (patient_id, 'Prescription Slip', 'Prescriptions', 'Clinical Prescription - Seasonal Fever', '2024-07-20', 'Dr. Amit Verma Clinic', 'prescription_jul2024.pdf', 'backend/uploads/reports/sample_rx.pdf', 210400, 'Rx: Paracetamol 650mg SOS for fever. Cetirizine 10mg once at night for 5 days. Hydration.', 'Prescribed symptomatic medication for viral rhinitis.'),
            (patient_id, 'Routine Urine Test', 'Other', 'Routine Urine Examination', '2024-06-05', 'Lal PathLabs', 'urine_test_jun2024.pdf', 'backend/uploads/reports/sample_urine.pdf', 190450, 'Color: Pale Yellow. Specific Gravity: 1.018. Protein: Nil. Glucose: Nil.', 'Routine urine test is completely within normal physiological limits.')
        ]

        for p_id, title, cat, test, dt, lab, fname, fpath, fsize, raw, interp in reports:
            rep_id = database.insert(
                conn,
                """INSERT INTO medical_reports 
                   (patient_user_id, report_title, report_category, test_name, test_date, issuing_lab_or_hospital, file_name, file_storage_path, file_size_bytes, extracted_raw_text, doctor_interpretation)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (p_id, title, cat, test, dt, lab, fname, fpath, fsize, raw, interp)
            )
            # Add summary for report 1
            if title == 'Blood Test Report':
                database.execute(
                    conn,
                    """INSERT INTO report_summaries (report_id, ai_summary_text, key_findings, normal_metrics, abnormal_metrics, questions_for_doctor)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (rep_id,
                     'Your complete blood count indicates healthy red blood cells, white blood cells, and platelets. Fasting blood sugar is within normal healthy limits. However, your Vitamin D level is slightly below the recommended range (18.2 ng/mL vs normal 30-100 ng/mL).',
                     'Healthy blood cell counts; Vitamin D deficiency detected.',
                     'Hemoglobin 14.2 g/dL, WBC 7,200 /uL, Platelets 240,000 /uL, Fasting Glucose 94 mg/dL',
                     'Serum Vitamin D: 18.2 ng/mL (Low)',
                     'Should I begin a weekly 60,000 IU Vitamin D3 supplement?')
                )
                measurements = [
                    (rep_id, 'Hemoglobin', 14.2, 'g/dL', 13.0, 17.0, 'Normal'),
                    (rep_id, 'Total WBC', 7200.0, '/uL', 4000.0, 11000.0, 'Normal'),
                    (rep_id, 'Platelets', 240000.0, '/uL', 150000.0, 450000.0, 'Normal'),
                    (rep_id, 'Fasting Blood Sugar', 94.0, 'mg/dL', 70.0, 100.0, 'Normal'),
                    (rep_id, 'Vitamin D (25-OH)', 18.2, 'ng/mL', 30.0, 100.0, 'Low'),
                    (rep_id, 'Serum Creatinine', 0.9, 'mg/dL', 0.7, 1.3, 'Normal'),
                ]
                for m in measurements:
                    database.execute(
                        conn,
                        "INSERT INTO report_extracted_measurements (report_id, test_metric_name, observed_value, unit, reference_range_low, reference_range_high, status_flag) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        m
                    )

    # 4. Timeline Events
    tl_count = database.fetch_one(conn, "SELECT COUNT(*) as c FROM health_timeline_events WHERE patient_user_id = ?", (patient_id,))
    if tl_count['c'] == 0:
        events = [
            (patient_id, 'Report Upload', 'Blood Test Report', '2024-10-15', '11:42 AM', 'Complete Blood Count: All values within normal range except Vitamin D (low).', 'Max Diagnostic Laboratory', 1, 'Completed'),
            (patient_id, 'AI Consultation', 'AI Symptom Consultation', '2024-10-02', '10:30 AM', 'Headache & Tension: Discussed headache symptoms with AI assistant. Advised rest and hydration.', 'AI Health Assistant', 1, 'Completed'),
            (patient_id, 'Report Upload', 'Chest X-Ray Report', '2024-09-28', '04:15 PM', 'Chest X-Ray: Clear lungs, normal cardiac size.', 'Apollo Imaging Center', 2, 'Completed'),
            (patient_id, 'Doctor Consultation', 'Doctor Follow-up Visit', '2024-07-20', '06:00 PM', 'Dr. Amit Verma (General Physician): Follow-up for fever. Prescribed medication.', 'Dr. Amit Verma Clinic', 4, 'Completed'),
            (patient_id, 'Report Upload', 'Routine Urine Test Report', '2024-06-05', '09:10 AM', 'Routine Urine Examination: Normal results.', 'Lal PathLabs', 5, 'Completed'),
        ]
        for ev in events:
            database.execute(
                conn,
                "INSERT INTO health_timeline_events (patient_user_id, event_type, event_title, event_date, event_time, short_description, organization_or_doctor, record_reference_id, status_badge) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ev
            )

    # 5. Medicine Reminders
    rem_count = database.fetch_one(conn, "SELECT COUNT(*) as c FROM medicine_reminders WHERE patient_user_id = ?", (patient_id,))
    if rem_count['c'] == 0:
        reminders = [
            (patient_id, 'Vitamin D3 (Cholecalciferol 60K)', '1 capsule', '09:00', 'Sunday', '2024-10-15', 1),
            (patient_id, 'Cetirizine 10mg', '1 tablet', '21:00', 'Daily', '2024-10-15', 1)
        ]
        for r in reminders:
            database.execute(
                conn,
                "INSERT INTO medicine_reminders (patient_user_id, medicine_name, dosage, reminder_time, days_of_week, start_date, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                r
            )

    database.close_connection(conn)
    print("Seeding completed successfully.")

if __name__ == '__main__':
    seed()
