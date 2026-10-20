import os
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.config.settings import settings

logger = logging.getLogger("ai_health_clinic.database")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0].lower()] = row[idx]
    return d

class DatabaseManager:
    def __init__(self):
        self.engine = settings.DB_ENGINE.lower()
        self.oracle_pool = None
        
        if self.engine == "oracle":
            try:
                import oracledb
                logger.info(f"Initializing Oracle connection to {settings.ORACLE_DSN}...")
                self.oracle_pool = oracledb.create_pool(
                    user=settings.ORACLE_USER,
                    password=settings.ORACLE_PASSWORD,
                    dsn=settings.ORACLE_DSN,
                    min=1,
                    max=5,
                    increment=1
                )
                logger.info("Oracle connection pool initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not connect to Oracle ({e}). Falling back to local SQLite engine for development.")
                self.engine = "sqlite"

    def get_connection(self):
        if self.engine == "oracle" and self.oracle_pool:
            import oracledb
            return self.oracle_pool.acquire()
        else:
            conn = sqlite3.connect(settings.DB_FILE, check_same_thread=False)
            conn.row_factory = dict_factory
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

    def query_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # If oracle, translate ? to :1, :2 if needed, or maintain consistency
            if self.engine == "oracle":
                cursor.execute(sql, params)
                columns = [col[0].lower() for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            if self.engine == "oracle":
                conn.close()
            else:
                conn.close()

    def query_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        results = self.query_all(sql, params)
        return results[0] if results else None

    def execute_write(self, sql: str, params: tuple = ()) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid if hasattr(cursor, 'lastrowid') else 0
        finally:
            conn.close()

    def execute_script(self, script_text: str):
        conn = self.get_connection()
        try:
            if self.engine == "oracle":
                cursor = conn.cursor()
                statements = script_text.split(";")
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt:
                        cursor.execute(stmt)
                conn.commit()
            else:
                conn.executescript(script_text)
                conn.commit()
        finally:
            conn.close()

db_manager = DatabaseManager()

def get_db():
    return db_manager

def init_database():
    """Initializes tables and seeds initial synthetic data if not already present."""
    logger.info("Checking and initializing database tables...")
    
    # SQLite schema equivalent to Oracle DDL
    schema_script = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('patient', 'doctor', 'admin')),
        full_name TEXT NOT NULL,
        phone TEXT,
        is_active INTEGER DEFAULT 1,
        is_verified INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS patient_profiles (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        date_of_birth TEXT,
        gender TEXT,
        blood_group TEXT,
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        known_allergies TEXT,
        chronic_conditions TEXT,
        current_medications TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS doctor_profiles (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        specialization TEXT NOT NULL,
        qualification_summary TEXT NOT NULL,
        experience_years INTEGER DEFAULT 0,
        medical_reg_number TEXT NOT NULL UNIQUE,
        registration_council TEXT NOT NULL,
        consultation_fee REAL DEFAULT 0.0,
        verification_status TEXT DEFAULT 'Pending',
        bio TEXT,
        rating REAL DEFAULT 5.0,
        total_reviews INTEGER DEFAULT 0,
        avatar_url TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS doctor_applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Pending',
        submitted_on TEXT DEFAULT CURRENT_TIMESTAMP,
        reviewed_by_admin_id INTEGER,
        review_notes TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(doctor_id) REFERENCES doctor_profiles(doctor_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS doctor_verification_evidence (
        evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        document_type TEXT NOT NULL,
        file_name TEXT NOT NULL,
        storage_path TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        ocr_extracted_text TEXT,
        verification_result TEXT DEFAULT 'Pending',
        FOREIGN KEY(application_id) REFERENCES doctor_applications(application_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS doctor_verification_reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        admin_user_id INTEGER NOT NULL,
        action_taken TEXT NOT NULL,
        reason_description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(application_id) REFERENCES doctor_applications(application_id) ON DELETE CASCADE,
        FOREIGN KEY(admin_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS medical_reports (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        report_title TEXT NOT NULL,
        report_category TEXT DEFAULT 'Other',
        test_name TEXT,
        test_date TEXT,
        report_issue_date TEXT,
        upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
        issuing_lab_or_hospital TEXT,
        file_name TEXT NOT NULL,
        file_storage_path TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        file_mime_type TEXT NOT NULL,
        processing_status TEXT DEFAULT 'Completed',
        extracted_raw_text TEXT,
        doctor_interpretation TEXT,
        doctor_follow_up_notes TEXT,
        version_number INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS report_summaries (
        summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL UNIQUE,
        ai_summary_text TEXT NOT NULL,
        key_findings TEXT,
        normal_metrics TEXT,
        abnormal_metrics TEXT,
        questions_for_doctor TEXT,
        source_grounding_disclaimer TEXT DEFAULT 'AI-generated summary based strictly on document text. Not a clinical diagnosis.',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(report_id) REFERENCES medical_reports(report_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS report_extracted_measurements (
        measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        test_metric_name TEXT NOT NULL,
        observed_value REAL NOT NULL,
        unit TEXT NOT NULL,
        reference_range_low REAL,
        reference_range_high REAL,
        status_flag TEXT DEFAULT 'Normal',
        notes TEXT,
        FOREIGN KEY(report_id) REFERENCES medical_reports(report_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ai_consultations (
        consultation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        session_title TEXT DEFAULT 'General Consultation',
        chief_complaint TEXT,
        triage_level TEXT DEFAULT 'Routine',
        summary TEXT,
        recommended_action TEXT,
        medical_sources_cited TEXT,
        started_at TEXT DEFAULT CURRENT_TIMESTAMP,
        ended_at TEXT,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ai_consultation_messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        consultation_id INTEGER NOT NULL,
        sender_role TEXT NOT NULL,
        message_content TEXT NOT NULL,
        is_urgent_warning INTEGER DEFAULT 0,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(consultation_id) REFERENCES ai_consultations(consultation_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        consultation_type TEXT DEFAULT 'Online',
        status TEXT DEFAULT 'Confirmed',
        reason_for_visit TEXT,
        doctor_notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctor_profiles(doctor_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS doctor_availability (
        availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        day_of_week TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY(doctor_id) REFERENCES doctor_profiles(doctor_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS patient_health_observations (
        observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        observation_date TEXT DEFAULT CURRENT_DATE,
        observation_type TEXT NOT NULL,
        measured_value TEXT NOT NULL,
        unit TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS medicines (
        medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        generic_name TEXT NOT NULL,
        brand_names TEXT,
        drug_class TEXT,
        common_uses TEXT,
        dosage_forms TEXT,
        precautions TEXT,
        contraindications TEXT,
        potential_side_effects TEXT,
        interaction_warnings TEXT,
        is_prescription_required INTEGER DEFAULT 0,
        source_reference TEXT
    );

    CREATE TABLE IF NOT EXISTS prescriptions (
        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_id INTEGER,
        diagnosis TEXT NOT NULL,
        instructions TEXT,
        date_issued TEXT DEFAULT CURRENT_DATE,
        valid_until TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctor_profiles(doctor_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS prescription_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prescription_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        duration TEXT NOT NULL,
        special_instructions TEXT,
        FOREIGN KEY(prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS medicine_reminders (
        reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        days_of_week TEXT DEFAULT 'Daily',
        start_date TEXT DEFAULT CURRENT_DATE,
        end_date TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS pharmacy_providers (
        provider_id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_name TEXT NOT NULL UNIQUE,
        base_url TEXT NOT NULL,
        search_url_template TEXT,
        category_tag TEXT DEFAULT 'Pharmacy',
        is_active INTEGER DEFAULT 1,
        integration_status TEXT DEFAULT 'External Link Only',
        logo_url TEXT,
        disclaimer_text TEXT
    );

    CREATE TABLE IF NOT EXISTS health_timeline_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        event_type TEXT NOT NULL,
        event_title TEXT NOT NULL,
        event_date TEXT NOT NULL,
        event_time TEXT,
        short_description TEXT,
        organization_or_doctor TEXT,
        record_reference_id INTEGER,
        status_badge TEXT DEFAULT 'Completed',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action_performed TEXT NOT NULL,
        resource_accessed TEXT,
        ip_address TEXT,
        status TEXT DEFAULT 'SUCCESS',
        details TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS record_sharing_permissions (
        permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_user_id INTEGER NOT NULL,
        doctor_user_id INTEGER NOT NULL,
        can_view_reports INTEGER DEFAULT 1,
        can_view_timeline INTEGER DEFAULT 1,
        can_view_medicines INTEGER DEFAULT 1,
        expires_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    
    db = get_db()
    if db.engine == "sqlite":
        db.execute_script(schema_script)
        
        # Check if users already seeded
        user_count = db.query_one("SELECT COUNT(*) as count FROM users")
        if user_count and user_count["count"] == 0:
            logger.info("Seeding synthetic users and clinic data...")
            seed_data(db)

def seed_data(db):
    import bcrypt
    pwd_hash = bcrypt.hashpw(b"Password@123", bcrypt.gensalt()).decode("utf-8")
    
    # 1. Users
    users = [
        (1, 'patient@clinic.com', pwd_hash, 'patient', 'Rohan Sharma', '+91 98765 43210', 1, 1),
        (2, 'doctor@clinic.com', pwd_hash, 'doctor', 'Dr. Amit Verma', '+91 98111 22233', 1, 1),
        (3, 'dr.priya@clinic.com', pwd_hash, 'doctor', 'Dr. Priya Mehta', '+91 98222 33344', 1, 1),
        (4, 'dr.rahul@clinic.com', pwd_hash, 'doctor', 'Dr. Rahul Singh', '+91 98333 44455', 1, 1),
        (5, 'dr.neha@clinic.com', pwd_hash, 'doctor', 'Dr. Neha Kapoor', '+91 98444 55566', 1, 1),
        (6, 'admin@clinic.com', pwd_hash, 'admin', 'System Administrator', '+91 99000 11223', 1, 1),
        (7, 'dr.rakesh@clinic.com', pwd_hash, 'doctor', 'Dr. Rakesh Kumar', '+91 98555 66677', 1, 0),
        (8, 'dr.sneha@clinic.com', pwd_hash, 'doctor', 'Dr. Sneha Patel', '+91 98666 77788', 1, 0),
        (9, 'dr.arjun@clinic.com', pwd_hash, 'doctor', 'Dr. Arjun Mehta', '+91 98777 88899', 1, 0),
        (10, 'dr.pooja@clinic.com', pwd_hash, 'doctor', 'Dr. Pooja Singh', '+91 98888 99900', 1, 0),
        (11, 'dr.karan@clinic.com', pwd_hash, 'doctor', 'Dr. Karan Shah', '+91 98999 00011', 1, 0),
    ]
    for u in users:
        db.execute_write("INSERT INTO users (user_id, email, password_hash, role, full_name, phone, is_active, is_verified) VALUES (?,?,?,?,?,?,?,?)", u)

    # 2. Patient Profile
    db.execute_write("""
        INSERT INTO patient_profiles (patient_id, user_id, date_of_birth, gender, blood_group, emergency_contact_name, emergency_contact_phone, known_allergies, chronic_conditions, current_medications)
        VALUES (1, 1, '1994-08-14', 'Male', 'B+', 'Anita Sharma', '+91 98765 00000', 'Penicillin', 'Mild Seasonal Asthma', 'Vitamin D3 60,000 IU once weekly')
    """)

    # 3. Doctor Profiles
    doc_profiles = [
        (1, 2, 'General Physician', 'MBBS, MD (Internal Medicine)', 8, 'DMC-2016-8941', 'Delhi Medical Council', 600.00, 'Verified', 'Specialist in preventive medicine and chronic disease management.', 4.9, 142),
        (2, 3, 'Cardiologist', 'MBBS, MD, DM (Cardiology)', 10, 'MMC-2014-4512', 'Maharashtra Medical Council', 1000.00, 'Verified', 'Cardiovascular specialist focusing on hypertension and heart wellness.', 4.8, 120),
        (3, 4, 'General Physician', 'MBBS', 8, 'KMC-2016-7781', 'Karnataka Medical Council', 500.00, 'Verified', 'Experienced general practitioner providing comprehensive health care.', 4.7, 35),
        (4, 5, 'Dermatologist', 'MBBS, MD (Dermatology)', 6, 'DMC-2018-9923', 'Delhi Medical Council', 800.00, 'Verified', 'Consultant dermatologist managing skin, hair, and complex allergies.', 4.6, 92),
        (5, 7, 'General Physician', 'MBBS, MD', 7, 'UPMC-2017-3312', 'Uttar Pradesh Medical Council', 500.00, 'Pending', 'General practitioner with rural medicine experience.', 5.0, 0),
        (6, 8, 'Dermatologist', 'MBBS, DNB', 5, 'GMC-2019-1120', 'Gujarat Medical Council', 700.00, 'Pending', 'Clinical dermatologist.', 5.0, 0),
        (7, 9, 'Orthopedic Surgeon', 'MBBS, MS (Ortho)', 9, 'MMC-2015-8841', 'Maharashtra Medical Council', 900.00, 'Pending', 'Joint and bone specialist.', 5.0, 0),
        (8, 10, 'Cardiologist', 'MBBS, MD, DM', 8, 'TNC-2016-5542', 'Tamil Nadu Medical Council', 1100.00, 'Pending', 'Cardiology researcher and consultant.', 5.0, 0),
        (9, 11, 'Pediatrician', 'MBBS, DCH', 6, 'WBMC-2018-6671', 'West Bengal Medical Council', 600.00, 'Pending', 'Child and adolescent healthcare.', 5.0, 0),
    ]
    for d in doc_profiles:
        db.execute_write("INSERT INTO doctor_profiles (doctor_id, user_id, specialization, qualification_summary, experience_years, medical_reg_number, registration_council, consultation_fee, verification_status, bio, rating, total_reviews) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", d)

    # 4. Applications for Admin Queue (Pending)
    apps = [
        (1, 5, 'Pending', '2024-10-15 09:30:00'),
        (2, 6, 'Pending', '2024-10-14 11:20:00'),
        (3, 7, 'Pending', '2024-10-12 14:15:00'),
        (4, 8, 'Pending', '2024-10-10 16:45:00'),
        (5, 9, 'Pending', '2024-10-08 10:10:00'),
    ]
    for a in apps:
        db.execute_write("INSERT INTO doctor_applications (application_id, doctor_id, status, submitted_on) VALUES (?,?,?,?)", a)

    # 5. Medical Reports for Rohan Sharma (User ID 1)
    reports = [
        (1, 1, 'Blood Test Report', 'Blood Tests', 'Complete Blood Count (CBC) & Vitamin Panel', '2024-10-15', '2024-10-15', '2024-10-15 11:42:00', 'Max Diagnostic Laboratory', 'cbc_report_oct2024.pdf', 'backend/uploads/reports/sample_cbc.pdf', 345120, 'application/pdf', 'Completed', 'Hemoglobin: 14.2 g/dL. Total WBC: 7,200 /uL. Platelets: 240,000 /uL. Fasting Blood Sugar: 94 mg/dL. Serum Vitamin D (25-OH): 18.2 ng/mL (Deficient). Creatinine: 0.9 mg/dL.', 'CBC parameters within normal range. Mild Vitamin D insufficiency observed.'),
        (2, 1, 'Chest X-Ray', 'Imaging', 'PA View Chest Radiograph', '2024-09-28', '2024-09-28', '2024-09-28 16:15:00', 'Apollo Imaging Center', 'chest_xray_sep2024.jpg', 'backend/uploads/reports/sample_xray.jpg', 1250440, 'image/jpeg', 'Completed', 'Bilateral lung fields clear. Normal cardiothoracic ratio. Costophrenic and cardiophrenic angles sharp. No active parenchymal lesion detected.', 'Clear chest radiograph. No evidence of infection or cardiomegaly.'),
        (3, 1, 'MRI Report', 'Imaging', 'Brain MRI Screening', '2024-08-12', '2024-08-12', '2024-08-12 10:20:00', 'Medanta Diagnostic Center', 'brain_mri_aug2024.pdf', 'backend/uploads/reports/sample_mri.pdf', 840210, 'application/pdf', 'Completed', 'Normal brain parenchyma. No intracranial hemorrhage or acute infarct detected.', 'Normal brain MRI screening report.'),
        (4, 1, 'Prescription', 'Prescriptions', 'Clinical Prescription - Fever & Allergy Follow-up', '2024-07-20', '2024-07-20', '2024-07-20 18:05:00', 'Dr. Amit Verma Clinic', 'prescription_jul2024.pdf', 'backend/uploads/reports/sample_rx.pdf', 210400, 'application/pdf', 'Completed', 'Rx: Paracetamol 650mg SOS for fever. Cetirizine 10mg once at night for 5 days. Adequate hydration.', 'Prescribed symptomatic medication for seasonal viral rhinitis.'),
        (5, 1, 'Urine Test', 'Other', 'Routine Urine Examination', '2024-06-05', '2024-06-05', '2024-06-05 09:10:00', 'Lal PathLabs', 'urine_test_jun2024.pdf', 'backend/uploads/reports/sample_urine.pdf', 190450, 'application/pdf', 'Completed', 'Color: Pale Yellow. Specific Gravity: 1.018. Protein: Nil. Glucose: Nil. Pus cells: 1-2 /HPF.', 'Routine urine test is completely within normal physiological limits.')
    ]
    for r in reports:
        db.execute_write("INSERT INTO medical_reports (report_id, patient_user_id, report_title, report_category, test_name, test_date, report_issue_date, upload_date, issuing_lab_or_hospital, file_name, file_storage_path, file_size_bytes, file_mime_type, processing_status, extracted_raw_text, doctor_interpretation) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", r)

    # 6. Report Summary (AI Grounded)
    db.execute_write("""
        INSERT INTO report_summaries (summary_id, report_id, ai_summary_text, key_findings, normal_metrics, abnormal_metrics, questions_for_doctor)
        VALUES (1, 1, 'Your Complete Blood Count is predominantly normal with healthy Hemoglobin (14.2 g/dL) and white blood cell levels. However, your Serum Vitamin D level is 18.2 ng/mL, which falls below the recommended minimum of 30 ng/mL, indicating mild deficiency.',
        'Hemoglobin, White Blood Cells, Platelets, and Blood Sugar are within healthy limits. Vitamin D is low.',
        'Hemoglobin (14.2 g/dL), WBC (7,200/uL), Platelets (240k/uL), Fasting Glucose (94 mg/dL)',
        'Serum 25-OH Vitamin D (18.2 ng/mL, Reference: 30 - 100 ng/mL)',
        '1. Should I take a weekly cholecalciferol supplement? 2. When should I repeat the 25-OH Vitamin D test?')
    """)

    # 7. Measurements for Report 1
    measurements = [
        (1, 1, 'Hemoglobin', 14.2, 'g/dL', 13.0, 17.0, 'Normal'),
        (2, 1, 'Total Leukocytes (WBC)', 7200, '/uL', 4000, 11000, 'Normal'),
        (3, 1, 'Platelet Count', 240000, '/uL', 150000, 450000, 'Normal'),
        (4, 1, 'Fasting Blood Sugar', 94.0, 'mg/dL', 70.0, 99.0, 'Normal'),
        (5, 1, 'Vitamin D (25-OH)', 18.2, 'ng/mL', 30.0, 100.0, 'Low')
    ]
    for m in measurements:
        db.execute_write("INSERT INTO report_extracted_measurements (measurement_id, report_id, test_metric_name, observed_value, unit, reference_range_low, reference_range_high, status_flag) VALUES (?,?,?,?,?,?,?,?)", m)

    # 8. AI Consultation
    db.execute_write("""
        INSERT INTO ai_consultations (consultation_id, patient_user_id, session_title, chief_complaint, triage_level, summary, recommended_action, medical_sources_cited)
        VALUES (1, 1, 'Headache Assessment', 'Mild headache since yesterday', 'Routine',
        'Patient reports mild bilateral headache persisting since yesterday without focal neurological deficits, visual changes, or neck stiffness.',
        'Advised rest, adequate oral hydration, and avoidance of prolonged digital screen time. Monitor for warning signs.',
        'NHS Guidelines on Tension-Type Headaches; Mayo Clinic Neurological Assessment.')
    """)
    messages = [
        (1, 1, 'assistant', 'Hello! I am your AI health assistant. Please tell me your symptoms or health concern, and I will ask a few questions to understand better.', '2024-10-19 10:23:00'),
        (2, 1, 'user', 'I have a headache since yesterday.', '2024-10-19 10:24:00'),
        (3, 1, 'assistant', 'I understand. Can you tell me: When did the headache start? Is it mild, moderate or severe? Do you have any other symptoms like fever, nausea or vision changes?', '2024-10-19 10:24:30')
    ]
    for msg in messages:
        db.execute_write("INSERT INTO ai_consultation_messages (message_id, consultation_id, sender_role, message_content, timestamp) VALUES (?,?,?,?,?)", msg)

    # 9. Appointments
    db.execute_write("""
        INSERT INTO appointments (appointment_id, patient_user_id, doctor_id, appointment_date, appointment_time, consultation_type, status, reason_for_visit, doctor_notes)
        VALUES (1, 1, 2, '2024-10-19', '11:00 AM', 'Online', 'Confirmed', 'Routine cardiovascular checkup and blood report review.', 'Patient advised to monitor blood pressure daily for 1 week.')
    """)
    db.execute_write("""
        INSERT INTO appointments (appointment_id, patient_user_id, doctor_id, appointment_date, appointment_time, consultation_type, status, reason_for_visit)
        VALUES (2, 1, 1, '2024-10-24', '02:00 PM', 'In-Person', 'Confirmed', 'Seasonal wellness check.')
    """)

    # 10. Unified Health Timeline Events (Authoritative Ledger)
    timeline_events = [
        (1, 1, 'Report Upload', 'Blood Test Report', '2024-10-15', '11:42 AM', 'Complete Blood Count: All values within normal range except Vitamin D (low).', 'Max Diagnostic Laboratory', 1, 'Completed'),
        (2, 1, 'AI Consultation', 'AI Consultation', '2024-10-02', '10:30 AM', 'Headache: Discussed headache symptoms. Advised rest and hydration.', 'AI Health Assistant', 1, 'Completed'),
        (3, 1, 'Report Upload', 'X-Ray Report', '2024-09-28', '04:15 PM', 'Chest X-Ray: No significant abnormality detected.', 'Apollo Imaging Center', 2, 'Completed'),
        (4, 1, 'Doctor Consultation', 'Doctor Consultation', '2024-07-20', '06:00 PM', 'Dr. Amit Verma (General Physician): Follow-up for fever. Prescribed medication.', 'Dr. Amit Verma Clinic', 4, 'Completed'),
        (5, 1, 'Report Upload', 'Urine Test Report', '2024-06-05', '09:10 AM', 'Routine Urine Examination: Normal results.', 'Lal PathLabs', 5, 'Completed')
    ]
    for t in timeline_events:
        db.execute_write("INSERT INTO health_timeline_events (event_id, patient_user_id, event_type, event_title, event_date, event_time, short_description, organization_or_doctor, record_reference_id, status_badge) VALUES (?,?,?,?,?,?,?,?,?,?)", t)

    # 11. Medicines
    medicines = [
        (1, 'Paracetamol (Acetaminophen)', 'Crocin, Calpol, Dolo 650', 'Analgesic & Antipyretic', 'Mild-to-moderate pain relief, fever reduction.', 'Tablet (500mg, 650mg), Syrup', 'Do not exceed 4,000 mg in 24 hours. Avoid concurrent alcohol use.', 'Severe hepatic impairment or active liver disease.', 'Nausea, rash (rare), hepatic toxicity with overdose.', 'Interacts with Warfarin at sustained high doses.', 0, 'British National Formulary (BNF); WHO Model List of Essential Medicines.'),
        (2, 'Amoxicillin', 'Mox, Novamox, Amoxil', 'Beta-lactam Antibiotic', 'Bacterial respiratory infections, ear-nose-throat infections, skin infections.', 'Capsule (250mg, 500mg), Suspension', 'Must be taken strictly as prescribed. Complete full course. Not effective against viral colds or flu.', 'Hypersensitivity to Penicillins or Cephalosporins.', 'Diarrhea, nausea, allergic rash.', 'May reduce efficacy of oral contraceptives; methotrexate interaction.', 1, 'WHO Essential Medicines List; National Formulary of India.'),
        (3, 'Metformin', 'Glycomet, Glucophage', 'Biguanide Antidiabetic', 'Management of Type 2 Diabetes Mellitus.', 'Tablet (500mg, 850mg, 1000mg SR)', 'Take with meals to minimize gastrointestinal discomfort. Monitor renal function periodically.', 'Severe renal failure (eGFR < 30 mL/min), acute metabolic acidosis.', 'Diarrhea, bloating, metallic taste, rare lactic acidosis.', 'Iodinated radiocontrast agents; heavy alcohol consumption.', 1, 'American Diabetes Association (ADA) Guidelines; CDSCO Prescribing Info.'),
        (4, 'Atorvastatin', 'Lipitor, Atorva, Storvas', 'HMG-CoA Reductase Inhibitor (Statin)', 'Hypercholesterolemia, prevention of cardiovascular disease.', 'Tablet (10mg, 20mg, 40mg)', 'Report unexplained muscle pain or tenderness immediately. Avoid excessive grapefruit juice.', 'Active liver disease, pregnancy, lactation.', 'Headache, myalgia, elevated liver enzymes.', 'Strong CYP3A4 inhibitors (clarithromycin, itraconazole), cyclosporine.', 1, 'AHA/ACC Cholesterol Clinical Guidelines.'),
        (5, 'Cetirizine', 'Cetzine, Zyrtec, Alerid', 'Second-generation Antihistamine', 'Allergic rhinitis, urticaria, seasonal sneezing and itch.', 'Tablet (10mg), Syrup (5mg/5mL)', 'May cause mild drowsiness in sensitive individuals. Avoid alcohol or heavy machinery.', 'Severe renal impairment (CrCl < 10 mL/min).', 'Somnolence, dry mouth, fatigue.', 'CNS depressants and alcohol may heighten sedation.', 0, 'NHS Health A-Z; Indian Pharmacopoeia.')
    ]
    for m in medicines:
        db.execute_write("INSERT INTO medicines (medicine_id, generic_name, brand_names, drug_class, common_uses, dosage_forms, precautions, contraindications, potential_side_effects, interaction_warnings, is_prescription_required, source_reference) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", m)

    # 12. Pharmacy Providers (7 Official Destinations)
    pharmacies = [
        (1, 'Amazon Pharmacy', 'https://www.amazon.in/pharmacy', 'https://www.amazon.in/s?k={query}&i=hpc', 'Online Pharmacy', 1, 'External Link Verified', 'External official pharmacy link. Live stock and prescription verification handled by Amazon.'),
        (2, 'Blinkit — Medicines', 'https://blinkit.com/cn/medicines/cid/287/7275', 'https://blinkit.com/s/?q={query}', 'Quick Delivery', 1, 'External Link Verified', 'External quick-commerce link. Item availability depends on local warehouse stock.'),
        (3, 'Swiggy Instamart', 'https://www.swiggy.com/instamart', 'https://www.swiggy.com/instamart/search?custom_back=true&query={query}', 'Quick Delivery', 1, 'External Link Verified', 'External quick-commerce link. Medicine range and delivery area varies by pin code.'),
        (4, 'Tata 1mg', 'https://www.1mg.com/', 'https://www.1mg.com/search/all?name={query}', 'Online Pharmacy', 1, 'External Link Verified', 'External online healthcare platform. Genuine prescription verification managed by Tata 1mg.'),
        (5, 'Apollo Pharmacy', 'https://www.apollopharmacy.in/', 'https://www.apollopharmacy.in/search-medicines/{query}', 'Retail & Online Pharmacy', 1, 'External Link Verified', 'External certified retail pharmacy network. Prices and availability subject to store location.'),
        (6, 'PharmEasy', 'https://pharmeasy.in/online-medicine-order', 'https://pharmeasy.in/search/all?name={query}', 'Online Pharmacy', 1, 'External Link Verified', 'External platform link. Prescription required for Schedule H/X drugs.'),
        (7, 'Netmeds', 'https://www.netmeds.com/c/', 'https://www.netmeds.com/catalogsearch/result?q={query}', 'Online Pharmacy', 1, 'External Link Verified', 'External medicine store link. Subject to Netmeds terms and conditions.')
    ]
    for p in pharmacies:
        db.execute_write("INSERT INTO pharmacy_providers (provider_id, provider_name, base_url, search_url_template, category_tag, is_active, integration_status, disclaimer_text) VALUES (?,?,?,?,?,?,?,?)", p)

    # 13. Medicine Reminders for Rohan Sharma
    db.execute_write("INSERT INTO medicine_reminders (reminder_id, patient_user_id, medicine_name, dosage, reminder_time, days_of_week, start_date, is_active) VALUES (?,?,?,?,?,?,?,?)",
                     (1, 1, 'Vitamin D3', '60,000 IU', '09:00', 'Sunday', '2024-10-15', 1))
    db.execute_write("INSERT INTO medicine_reminders (reminder_id, patient_user_id, medicine_name, dosage, reminder_time, days_of_week, start_date, is_active) VALUES (?,?,?,?,?,?,?,?)",
                     (2, 1, 'Cetirizine', '10 mg', '21:30', 'Daily', '2024-10-18', 1))

    logger.info("Database initialized and demo data seeded successfully.")
