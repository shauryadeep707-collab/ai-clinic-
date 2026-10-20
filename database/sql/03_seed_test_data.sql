-- ====================================================================
-- AI HEALTH CLINIC - ORACLE DATABASE SCHEMA
-- Script 03: Seed Synthetic Demonstration Data
-- Password for all seed users is 'Password@123' (hashed via bcrypt)
-- ====================================================================

-- 1. USERS
-- Rohan Sharma (Patient)
INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (1, 'patient@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'patient', 'Rohan Sharma', '+91 98765 43210', 1, 1);

-- Dr. Amit Verma (Doctor)
INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (2, 'doctor@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Amit Verma', '+91 98111 22233', 1, 1);

-- Dr. Priya Mehta (Doctor - Cardiologist)
INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (3, 'dr.priya@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Priya Mehta', '+91 98222 33344', 1, 1);

-- Dr. Rahul Singh (Doctor - General Physician)
INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (4, 'dr.rahul@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Rahul Singh', '+91 98333 44455', 1, 1);

-- Dr. Neha Kapoor (Doctor - Dermatologist)
INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (5, 'dr.neha@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Neha Kapoor', '+91 98444 55566', 1, 1);

-- Administrator
INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (6, 'admin@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'admin', 'System Administrator', '+91 99000 11223', 1, 1);

-- Pending Applicant Doctors for Admin Queue
INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (7, 'dr.rakesh@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Rakesh Kumar', '+91 98555 66677', 1, 0);

INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (8, 'dr.sneha@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Sneha Patel', '+91 98666 77788', 1, 0);

INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (9, 'dr.arjun@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Arjun Mehta', '+91 98777 88899', 1, 0);

INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (10, 'dr.pooja@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Pooja Singh', '+91 98888 99900', 1, 0);

INSERT INTO USERS (USER_ID, EMAIL, PASSWORD_HASH, ROLE, FULL_NAME, PHONE, IS_ACTIVE, IS_VERIFIED)
VALUES (11, 'dr.karan@clinic.com', '$2b$12$e0M2/p91e60XvR.Vp992o.aD3/3g7bS5C07xJmYJ8Yl00H1q7mP/a', 'doctor', 'Dr. Karan Shah', '+91 98999 00011', 1, 0);

-- 2. PATIENT PROFILES
INSERT INTO PATIENT_PROFILES (PATIENT_ID, USER_ID, DATE_OF_BIRTH, GENDER, BLOOD_GROUP, EMERGENCY_CONTACT_NAME, EMERGENCY_CONTACT_PHONE, KNOWN_ALLERGIES, CHRONIC_CONDITIONS, CURRENT_MEDICATIONS)
VALUES (1, 1, TO_DATE('1994-08-14', 'YYYY-MM-DD'), 'Male', 'B+', 'Anita Sharma', '+91 98765 00000', 'Penicillin', 'Mild Seasonal Asthma', 'Vitamin D3 60,000 IU once weekly');

-- 3. DOCTOR PROFILES
INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO, RATING, TOTAL_REVIEWS)
VALUES (1, 2, 'General Physician', 'MBBS, MD (Internal Medicine)', 8, 'DMC-2016-8941', 'Delhi Medical Council', 600.00, 'Verified', 'Specialist in preventive medicine, lifestyle disorders, and chronic disease management.', 4.9, 142);

INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO, RATING, TOTAL_REVIEWS)
VALUES (2, 3, 'Cardiologist', 'MBBS, MD, DM (Cardiology)', 10, 'MMC-2014-4512', 'Maharashtra Medical Council', 1000.00, 'Verified', 'Cardiovascular specialist focusing on hypertension, heart rhythm, and preventive cardiology.', 4.8, 120);

INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO, RATING, TOTAL_REVIEWS)
VALUES (3, 4, 'General Physician', 'MBBS', 8, 'KMC-2016-7781', 'Karnataka Medical Council', 500.00, 'Verified', 'Experienced general practitioner providing comprehensive health assessments and primary care.', 4.7, 35);

INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO, RATING, TOTAL_REVIEWS)
VALUES (4, 5, 'Dermatologist', 'MBBS, MD (Dermatology)', 6, 'DMC-2018-9923', 'Delhi Medical Council', 800.00, 'Verified', 'Dermatologist and aesthetic consultant handling skin, hair, and chronic dermatological conditions.', 4.6, 92);

-- Pending Doctors in Applications
INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO)
VALUES (5, 7, 'General Physician', 'MBBS, MD', 7, 'UPMC-2017-3312', 'Uttar Pradesh Medical Council', 500.00, 'Pending', 'General practitioner');

INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO)
VALUES (6, 8, 'Dermatologist', 'MBBS, DNB', 5, 'GMC-2019-1120', 'Gujarat Medical Council', 700.00, 'Pending', 'Consultant Dermatologist');

INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO)
VALUES (7, 9, 'Orthopedic Surgeon', 'MBBS, MS (Ortho)', 9, 'MMC-2015-8841', 'Maharashtra Medical Council', 900.00, 'Pending', 'Orthopedic surgeon and joint specialist');

INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO)
VALUES (8, 10, 'Cardiologist', 'MBBS, MD, DM', 8, 'TNC-2016-5542', 'Tamil Nadu Medical Council', 1100.00, 'Pending', 'Consultant Cardiologist');

INSERT INTO DOCTOR_PROFILES (DOCTOR_ID, USER_ID, SPECIALIZATION, QUALIFICATION_SUMMARY, EXPERIENCE_YEARS, MEDICAL_REG_NUMBER, REGISTRATION_COUNCIL, CONSULTATION_FEE, VERIFICATION_STATUS, BIO)
VALUES (9, 11, 'Pediatrician', 'MBBS, DCH', 6, 'WBMC-2018-6671', 'West Bengal Medical Council', 600.00, 'Pending', 'Pediatric child specialist');

-- 4. DOCTOR APPLICATIONS & VERIFICATION EVIDENCE
INSERT INTO DOCTOR_APPLICATIONS (APPLICATION_ID, DOCTOR_ID, STATUS, SUBMITTED_ON)
VALUES (1, 5, 'Pending', TO_TIMESTAMP('2024-10-15 09:30:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO DOCTOR_APPLICATIONS (APPLICATION_ID, DOCTOR_ID, STATUS, SUBMITTED_ON)
VALUES (2, 6, 'Pending', TO_TIMESTAMP('2024-10-14 11:20:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO DOCTOR_APPLICATIONS (APPLICATION_ID, DOCTOR_ID, STATUS, SUBMITTED_ON)
VALUES (3, 7, 'Pending', TO_TIMESTAMP('2024-10-12 14:15:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO DOCTOR_APPLICATIONS (APPLICATION_ID, DOCTOR_ID, STATUS, SUBMITTED_ON)
VALUES (4, 8, 'Pending', TO_TIMESTAMP('2024-10-10 16:45:00', 'YYYY-MM-DD HH24:MI:SS'));
INSERT INTO DOCTOR_APPLICATIONS (APPLICATION_ID, DOCTOR_ID, STATUS, SUBMITTED_ON)
VALUES (5, 9, 'Pending', TO_TIMESTAMP('2024-10-08 10:10:00', 'YYYY-MM-DD HH24:MI:SS'));

-- 5. MEDICAL REPORTS (For Rohan Sharma, User ID 1)
INSERT INTO MEDICAL_REPORTS (REPORT_ID, PATIENT_USER_ID, REPORT_TITLE, REPORT_CATEGORY, TEST_NAME, TEST_DATE, REPORT_ISSUE_DATE, UPLOAD_DATE, ISSUING_LAB_OR_HOSPITAL, FILE_NAME, FILE_STORAGE_PATH, FILE_SIZE_BYTES, FILE_MIME_TYPE, PROCESSING_STATUS, EXTRACTED_RAW_TEXT, DOCTOR_INTERPRETATION)
VALUES (
    1, 1, 'Blood Test Report', 'Blood Tests', 'Complete Blood Count (CBC) & Vitamin Panel',
    TO_DATE('2024-10-15', 'YYYY-MM-DD'), TO_DATE('2024-10-15', 'YYYY-MM-DD'),
    TO_TIMESTAMP('2024-10-15 11:42:00', 'YYYY-MM-DD HH24:MI:SS'),
    'Max Diagnostic Laboratory, New Delhi', 'cbc_report_oct2024.pdf', 'backend/uploads/reports/sample_cbc.pdf', 345120, 'application/pdf', 'Completed',
    'Hemoglobin: 14.2 g/dL. Total WBC: 7,200 /uL. Platelets: 240,000 /uL. Fasting Blood Sugar: 94 mg/dL. Serum Vitamin D (25-OH): 18.2 ng/mL (Deficient). Creatinine: 0.9 mg/dL.',
    'CBC parameters within normal range. Mild Vitamin D insufficiency observed. Advised 60,000 IU cholecalciferol weekly for 8 weeks.'
);

INSERT INTO MEDICAL_REPORTS (REPORT_ID, PATIENT_USER_ID, REPORT_TITLE, REPORT_CATEGORY, TEST_NAME, TEST_DATE, REPORT_ISSUE_DATE, UPLOAD_DATE, ISSUING_LAB_OR_HOSPITAL, FILE_NAME, FILE_STORAGE_PATH, FILE_SIZE_BYTES, FILE_MIME_TYPE, PROCESSING_STATUS, EXTRACTED_RAW_TEXT, DOCTOR_INTERPRETATION)
VALUES (
    2, 1, 'Chest X-Ray', 'Imaging', 'PA View Chest Radiograph',
    TO_DATE('2024-09-28', 'YYYY-MM-DD'), TO_DATE('2024-09-28', 'YYYY-MM-DD'),
    TO_TIMESTAMP('2024-09-28 16:15:00', 'YYYY-MM-DD HH24:MI:SS'),
    'Apollo Imaging Center', 'chest_xray_sep2024.jpg', 'backend/uploads/reports/sample_xray.jpg', 1250440, 'image/jpeg', 'Completed',
    'Bilateral lung fields clear. Normal cardiothoracic ratio. Costophrenic and cardiophrenic angles are sharp. No active parenchymal lesion detected.',
    'Clear chest radiograph. No evidence of infection, effusion or cardiomegaly.'
);

INSERT INTO MEDICAL_REPORTS (REPORT_ID, PATIENT_USER_ID, REPORT_TITLE, REPORT_CATEGORY, TEST_NAME, TEST_DATE, REPORT_ISSUE_DATE, UPLOAD_DATE, ISSUING_LAB_OR_HOSPITAL, FILE_NAME, FILE_STORAGE_PATH, FILE_SIZE_BYTES, FILE_MIME_TYPE, PROCESSING_STATUS, EXTRACTED_RAW_TEXT, DOCTOR_INTERPRETATION)
VALUES (
    3, 1, 'MRI Report', 'Imaging', 'Brain MRI Screening',
    TO_DATE('2024-08-12', 'YYYY-MM-DD'), TO_DATE('2024-08-12', 'YYYY-MM-DD'),
    TO_TIMESTAMP('2024-08-12 10:20:00', 'YYYY-MM-DD HH24:MI:SS'),
    'Medanta Diagnostic Center', 'brain_mri_aug2024.pdf', 'backend/uploads/reports/sample_mri.pdf', 840210, 'application/pdf', 'Completed',
    'Normal brain parenchyma. No intracranial hemorrhage or acute infarct detected. Ventricular system within normal limits for age.',
    'Normal brain MRI screening report.'
);

INSERT INTO MEDICAL_REPORTS (REPORT_ID, PATIENT_USER_ID, REPORT_TITLE, REPORT_CATEGORY, TEST_NAME, TEST_DATE, REPORT_ISSUE_DATE, UPLOAD_DATE, ISSUING_LAB_OR_HOSPITAL, FILE_NAME, FILE_STORAGE_PATH, FILE_SIZE_BYTES, FILE_MIME_TYPE, PROCESSING_STATUS, EXTRACTED_RAW_TEXT, DOCTOR_INTERPRETATION)
VALUES (
    4, 1, 'Prescription', 'Prescriptions', 'Clinical Prescription - Fever & Allergy Follow-up',
    TO_DATE('2024-07-20', 'YYYY-MM-DD'), TO_DATE('2024-07-20', 'YYYY-MM-DD'),
    TO_TIMESTAMP('2024-07-20 18:05:00', 'YYYY-MM-DD HH24:MI:SS'),
    'Dr. Amit Verma Clinic', 'prescription_jul2024.pdf', 'backend/uploads/reports/sample_rx.pdf', 210400, 'application/pdf', 'Completed',
    'Rx: Paracetamol 650mg SOS for fever. Cetirizine 10mg once at night for 5 days. Adequate hydration.',
    'Prescribed symptomatic medication for seasonal viral rhinitis.'
);

INSERT INTO MEDICAL_REPORTS (REPORT_ID, PATIENT_USER_ID, REPORT_TITLE, REPORT_CATEGORY, TEST_NAME, TEST_DATE, REPORT_ISSUE_DATE, UPLOAD_DATE, ISSUING_LAB_OR_HOSPITAL, FILE_NAME, FILE_STORAGE_PATH, FILE_SIZE_BYTES, FILE_MIME_TYPE, PROCESSING_STATUS, EXTRACTED_RAW_TEXT, DOCTOR_INTERPRETATION)
VALUES (
    5, 1, 'Urine Test', 'Other', 'Routine Urine Examination',
    TO_DATE('2024-06-05', 'YYYY-MM-DD'), TO_DATE('2024-06-05', 'YYYY-MM-DD'),
    TO_TIMESTAMP('2024-06-05 09:10:00', 'YYYY-MM-DD HH24:MI:SS'),
    'Lal PathLabs', 'urine_test_jun2024.pdf', 'backend/uploads/reports/sample_urine.pdf', 190450, 'application/pdf', 'Completed',
    'Color: Pale Yellow. Specific Gravity: 1.018. Protein: Nil. Glucose: Nil. Pus cells: 1-2 /HPF. Epithelial cells: Occasional.',
    'Routine urine test is completely within normal physiological limits.'
);

-- 6. REPORT SUMMARIES (AI Grounded)
INSERT INTO REPORT_SUMMARIES (SUMMARY_ID, REPORT_ID, AI_SUMMARY_TEXT, KEY_FINDINGS, NORMAL_METRICS, ABNORMAL_METRICS, QUESTIONS_FOR_DOCTOR)
VALUES (
    1, 1,
    'Your Complete Blood Count is predominantly normal with healthy Hemoglobin (14.2 g/dL) and white blood cell levels. However, your Serum Vitamin D level is 18.2 ng/mL, which falls below the recommended minimum of 30 ng/mL, indicating mild deficiency.',
    'Hemoglobin, White Blood Cells, Platelets, and Blood Sugar are within healthy limits. Vitamin D is low.',
    'Hemoglobin (14.2 g/dL), WBC (7,200/uL), Platelets (240k/uL), Fasting Glucose (94 mg/dL)',
    'Serum 25-OH Vitamin D (18.2 ng/mL, Reference: 30 - 100 ng/mL)',
    '1. Should I take a weekly cholecalciferol supplement? 2. When should I repeat the 25-OH Vitamin D test?'
);

-- 7. EXTRACTED MEASUREMENTS FOR REPORT 1
INSERT INTO REPORT_EXTRACTED_MEASUREMENTS (MEASUREMENT_ID, REPORT_ID, TEST_METRIC_NAME, OBSERVED_VALUE, UNIT, REFERENCE_RANGE_LOW, REFERENCE_RANGE_HIGH, STATUS_FLAG)
VALUES (1, 1, 'Hemoglobin', 14.2, 'g/dL', 13.0, 17.0, 'Normal');
INSERT INTO REPORT_EXTRACTED_MEASUREMENTS (MEASUREMENT_ID, REPORT_ID, TEST_METRIC_NAME, OBSERVED_VALUE, UNIT, REFERENCE_RANGE_LOW, REFERENCE_RANGE_HIGH, STATUS_FLAG)
VALUES (2, 1, 'Total Leukocytes (WBC)', 7200, '/uL', 4000, 11000, 'Normal');
INSERT INTO REPORT_EXTRACTED_MEASUREMENTS (MEASUREMENT_ID, REPORT_ID, TEST_METRIC_NAME, OBSERVED_VALUE, UNIT, REFERENCE_RANGE_LOW, REFERENCE_RANGE_HIGH, STATUS_FLAG)
VALUES (3, 1, 'Platelet Count', 240000, '/uL', 150000, 450000, 'Normal');
INSERT INTO REPORT_EXTRACTED_MEASUREMENTS (MEASUREMENT_ID, REPORT_ID, TEST_METRIC_NAME, OBSERVED_VALUE, UNIT, REFERENCE_RANGE_LOW, REFERENCE_RANGE_HIGH, STATUS_FLAG)
VALUES (4, 1, 'Fasting Blood Sugar', 94.0, 'mg/dL', 70.0, 99.0, 'Normal');
INSERT INTO REPORT_EXTRACTED_MEASUREMENTS (MEASUREMENT_ID, REPORT_ID, TEST_METRIC_NAME, OBSERVED_VALUE, UNIT, REFERENCE_RANGE_LOW, REFERENCE_RANGE_HIGH, STATUS_FLAG)
VALUES (5, 1, 'Vitamin D (25-OH)', 18.2, 'ng/mL', 30.0, 100.0, 'Low');

-- 8. AI CONSULTATION (Matching Image Screen 3)
INSERT INTO AI_CONSULTATIONS (CONSULTATION_ID, PATIENT_USER_ID, SESSION_TITLE, CHIEF_COMPLAINT, TRIAGE_LEVEL, SUMMARY, RECOMMENDED_ACTION, MEDICAL_SOURCES_CITED)
VALUES (
    1, 1, 'Headache Assessment', 'Mild headache since yesterday', 'Routine',
    'Patient reports mild bilateral headache persisting since yesterday without focal neurological deficits, visual changes, or neck stiffness.',
    'Advised rest, adequate oral hydration, and avoidance of prolonged digital screen time. Monitor for warning signs.',
    'NHS Guidelines on Tension-Type Headaches; Mayo Clinic Neurological Assessment.'
);

INSERT INTO AI_CONSULTATION_MESSAGES (MESSAGE_ID, CONSULTATION_ID, SENDER_ROLE, MESSAGE_CONTENT, TIMESTAMP)
VALUES (1, 1, 'assistant', 'Hello! I am your AI health assistant. Please tell me your symptoms or health concern, and I will ask a few questions to understand better.', TO_TIMESTAMP('2024-10-19 10:23:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO AI_CONSULTATION_MESSAGES (MESSAGE_ID, CONSULTATION_ID, SENDER_ROLE, MESSAGE_CONTENT, TIMESTAMP)
VALUES (2, 1, 'user', 'I have a headache since yesterday.', TO_TIMESTAMP('2024-10-19 10:24:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO AI_CONSULTATION_MESSAGES (MESSAGE_ID, CONSULTATION_ID, SENDER_ROLE, MESSAGE_CONTENT, TIMESTAMP)
VALUES (3, 1, 'assistant', 'I understand. Can you tell me: When did the headache start? Is it mild, moderate or severe? Do you have any other symptoms like fever, nausea or vision changes?', TO_TIMESTAMP('2024-10-19 10:24:30', 'YYYY-MM-DD HH24:MI:SS'));

-- 9. APPOINTMENTS
INSERT INTO APPOINTMENTS (APPOINTMENT_ID, PATIENT_USER_ID, DOCTOR_ID, APPOINTMENT_DATE, APPOINTMENT_TIME, CONSULTATION_TYPE, STATUS, REASON_FOR_VISIT, DOCTOR_NOTES)
VALUES (
    1, 1, 2, TO_DATE('2024-10-19', 'YYYY-MM-DD'), '11:00 AM', 'Online', 'Confirmed',
    'Routine cardiovascular checkup and blood report review.',
    'Patient advised to monitor blood pressure daily for 1 week and review lipid panel in 6 months.'
);

INSERT INTO APPOINTMENTS (APPOINTMENT_ID, PATIENT_USER_ID, DOCTOR_ID, APPOINTMENT_DATE, APPOINTMENT_TIME, CONSULTATION_TYPE, STATUS, REASON_FOR_VISIT)
VALUES (
    2, 1, 1, TO_DATE('2024-10-24', 'YYYY-MM-DD'), '02:00 PM', 'In-Person', 'Requested',
    'General seasonal wellness follow-up.'
);

-- 10. UNIFIED HEALTH TIMELINE EVENTS (Authoritative Ledger matching Screen 5)
INSERT INTO HEALTH_TIMELINE_EVENTS (EVENT_ID, PATIENT_USER_ID, EVENT_TYPE, EVENT_TITLE, EVENT_DATE, EVENT_TIME, SHORT_DESCRIPTION, ORGANIZATION_OR_DOCTOR, RECORD_REFERENCE_ID, STATUS_BADGE)
VALUES (
    1, 1, 'Report Upload', 'Blood Test Report', TO_DATE('2024-10-15', 'YYYY-MM-DD'), '11:42 AM',
    'Complete Blood Count: All values within normal range except Vitamin D (low).', 'Max Diagnostic Laboratory', 1, 'Completed'
);

INSERT INTO HEALTH_TIMELINE_EVENTS (EVENT_ID, PATIENT_USER_ID, EVENT_TYPE, EVENT_TITLE, EVENT_DATE, EVENT_TIME, SHORT_DESCRIPTION, ORGANIZATION_OR_DOCTOR, RECORD_REFERENCE_ID, STATUS_BADGE)
VALUES (
    2, 1, 'AI Consultation', 'AI Consultation', TO_DATE('2024-10-02', 'YYYY-MM-DD'), '10:30 AM',
    'Headache: Discussed headache symptoms. Advised rest and hydration.', 'AI Health Assistant', 1, 'Completed'
);

INSERT INTO HEALTH_TIMELINE_EVENTS (EVENT_ID, PATIENT_USER_ID, EVENT_TYPE, EVENT_TITLE, EVENT_DATE, EVENT_TIME, SHORT_DESCRIPTION, ORGANIZATION_OR_DOCTOR, RECORD_REFERENCE_ID, STATUS_BADGE)
VALUES (
    3, 1, 'Report Upload', 'X-Ray Report', TO_DATE('2024-09-28', 'YYYY-MM-DD'), '04:15 PM',
    'Chest X-Ray: No significant abnormality detected.', 'Apollo Imaging Center', 2, 'Completed'
);

INSERT INTO HEALTH_TIMELINE_EVENTS (EVENT_ID, PATIENT_USER_ID, EVENT_TYPE, EVENT_TITLE, EVENT_DATE, EVENT_TIME, SHORT_DESCRIPTION, ORGANIZATION_OR_DOCTOR, RECORD_REFERENCE_ID, STATUS_BADGE)
VALUES (
    4, 1, 'Doctor Consultation', 'Doctor Consultation', TO_DATE('2024-07-20', 'YYYY-MM-DD'), '06:00 PM',
    'Dr. Amit Verma (General Physician): Follow-up for fever. Prescribed medication.', 'Dr. Amit Verma Clinic', 4, 'Completed'
);

INSERT INTO HEALTH_TIMELINE_EVENTS (EVENT_ID, PATIENT_USER_ID, EVENT_TYPE, EVENT_TITLE, EVENT_DATE, EVENT_TIME, SHORT_DESCRIPTION, ORGANIZATION_OR_DOCTOR, RECORD_REFERENCE_ID, STATUS_BADGE)
VALUES (
    5, 1, 'Report Upload', 'Urine Test Report', TO_DATE('2024-06-05', 'YYYY-MM-DD'), '09:10 AM',
    'Routine Urine Examination: Normal results.', 'Lal PathLabs', 5, 'Completed'
);

-- 11. MEDICINES CATALOGUE (Educational & Safety Information)
INSERT INTO MEDICINES (MEDICINE_ID, GENERIC_NAME, BRAND_NAMES, DRUG_CLASS, COMMON_USES, DOSAGE_FORMS, PRECAUTIONS, CONTRAINDICATIONS, POTENTIAL_SIDE_EFFECTS, INTERACTION_WARNINGS, IS_PRESCRIPTION_REQUIRED, SOURCE_REFERENCE)
VALUES (
    1, 'Paracetamol (Acetaminophen)', 'Crocin, Calpol, Dolo 650', 'Analgesic & Antipyretic',
    'Mild-to-moderate pain relief, fever reduction.', 'Tablet (500mg, 650mg), Syrup',
    'Do not exceed 4,000 mg in 24 hours. Avoid concurrent alcohol use.',
    'Severe hepatic impairment or active liver disease.',
    'Nausea, rash (rare), hepatic toxicity with overdose.',
    'Interacts with Warfarin (long-term high doses may increase bleeding risk).',
    0, 'British National Formulary (BNF); WHO Model List of Essential Medicines.'
);

INSERT INTO MEDICINES (MEDICINE_ID, GENERIC_NAME, BRAND_NAMES, DRUG_CLASS, COMMON_USES, DOSAGE_FORMS, PRECAUTIONS, CONTRAINDICATIONS, POTENTIAL_SIDE_EFFECTS, INTERACTION_WARNINGS, IS_PRESCRIPTION_REQUIRED, SOURCE_REFERENCE)
VALUES (
    2, 'Amoxicillin', 'Mox, Novamox, Amoxil', 'Beta-lactam Antibiotic',
    'Bacterial respiratory infections, ear-nose-throat infections, skin infections.', 'Capsule (250mg, 500mg), Suspension',
    'Must be taken strictly as prescribed. Complete full course. Not effective against viral colds or flu.',
    'Hypersensitivity to Penicillins or Cephalosporins.',
    'Diarrhea, nausea, allergic rash.',
    'May reduce efficacy of oral contraceptives; methotrexate interaction.',
    1, 'WHO Essential Medicines List; National Formulary of India.'
);

INSERT INTO MEDICINES (MEDICINE_ID, GENERIC_NAME, BRAND_NAMES, DRUG_CLASS, COMMON_USES, DOSAGE_FORMS, PRECAUTIONS, CONTRAINDICATIONS, POTENTIAL_SIDE_EFFECTS, INTERACTION_WARNINGS, IS_PRESCRIPTION_REQUIRED, SOURCE_REFERENCE)
VALUES (
    3, 'Metformin', 'Glycomet, Glucophage', 'Biguanide Antidiabetic',
    'Management of Type 2 Diabetes Mellitus.', 'Tablet (500mg, 850mg, 1000mg SR)',
    'Take with meals to minimize gastrointestinal discomfort. Monitor renal function periodically.',
    'Severe renal failure (eGFR < 30 mL/min), acute metabolic acidosis.',
    'Diarrhea, bloating, metallic taste, rare lactic acidosis.',
    'Iodinated radiocontrast agents; heavy alcohol consumption.',
    1, 'American Diabetes Association (ADA) Guidelines; CDSCO Approved Prescribing Info.'
);

INSERT INTO MEDICINES (MEDICINE_ID, GENERIC_NAME, BRAND_NAMES, DRUG_CLASS, COMMON_USES, DOSAGE_FORMS, PRECAUTIONS, CONTRAINDICATIONS, POTENTIAL_SIDE_EFFECTS, INTERACTION_WARNINGS, IS_PRESCRIPTION_REQUIRED, SOURCE_REFERENCE)
VALUES (
    4, 'Atorvastatin', 'Lipitor, Atorva, Storvas', 'HMG-CoA Reductase Inhibitor (Statin)',
    'Hypercholesterolemia, prevention of cardiovascular disease.', 'Tablet (10mg, 20mg, 40mg)',
    'Report unexplained muscle pain or tenderness immediately. Avoid excessive grapefruit juice.',
    'Active liver disease, pregnancy, lactation.',
    'Headache, myalgia, elevated liver enzymes.',
    'Strong CYP3A4 inhibitors (clarithromycin, itraconazole), cyclosporine.',
    1, 'AHA/ACC Cholesterol Clinical Guidelines.'
);

INSERT INTO MEDICINES (MEDICINE_ID, GENERIC_NAME, BRAND_NAMES, DRUG_CLASS, COMMON_USES, DOSAGE_FORMS, PRECAUTIONS, CONTRAINDICATIONS, POTENTIAL_SIDE_EFFECTS, INTERACTION_WARNINGS, IS_PRESCRIPTION_REQUIRED, SOURCE_REFERENCE)
VALUES (
    5, 'Cetirizine', 'Cetzine, Zyrtec, Alerid', 'Second-generation Antihistamine',
    'Allergic rhinitis, urticaria, seasonal sneezing and itch.', 'Tablet (10mg), Syrup (5mg/5mL)',
    'May cause mild drowsiness in sensitive individuals. Avoid alcohol or heavy machinery.',
    'Severe renal impairment (CrCl < 10 mL/min).',
    'Somnolence, dry mouth, fatigue.',
    'CNS depressants and alcohol may heighten sedation.',
    0, 'NHS Health A-Z; Indian Pharmacopoeia.'
);

-- 12. PHARMACY PROVIDERS (Official verified destinations)
INSERT INTO PHARMACY_PROVIDERS (PROVIDER_ID, PROVIDER_NAME, BASE_URL, SEARCH_URL_TEMPLATE, CATEGORY_TAG, IS_ACTIVE, INTEGRATION_STATUS, DISCLAIMER_TEXT)
VALUES (
    1, 'Amazon Pharmacy', 'https://www.amazon.in/pharmacy', 'https://www.amazon.in/s?k={query}&i=hpc',
    'Online Pharmacy', 1, 'External Link Verified',
    'External official pharmacy link. Live stock and prescription verification handled by Amazon.'
);

INSERT INTO PHARMACY_PROVIDERS (PROVIDER_ID, PROVIDER_NAME, BASE_URL, SEARCH_URL_TEMPLATE, CATEGORY_TAG, IS_ACTIVE, INTEGRATION_STATUS, DISCLAIMER_TEXT)
VALUES (
    2, 'Blinkit — Medicines', 'https://blinkit.com/cn/medicines/cid/287/7275', 'https://blinkit.com/s/?q={query}',
    'Quick Delivery', 1, 'External Link Verified',
    'External quick-commerce link. Item availability depends on local warehouse stock.'
);

INSERT INTO PHARMACY_PROVIDERS (PROVIDER_ID, PROVIDER_NAME, BASE_URL, SEARCH_URL_TEMPLATE, CATEGORY_TAG, IS_ACTIVE, INTEGRATION_STATUS, DISCLAIMER_TEXT)
VALUES (
    3, 'Swiggy Instamart', 'https://www.swiggy.com/instamart', 'https://www.swiggy.com/instamart/search?custom_back=true&query={query}',
    'Quick Delivery', 1, 'External Link Verified',
    'External quick-commerce link. Medicine range and delivery area varies by pin code.'
);

INSERT INTO PHARMACY_PROVIDERS (PROVIDER_ID, PROVIDER_NAME, BASE_URL, SEARCH_URL_TEMPLATE, CATEGORY_TAG, IS_ACTIVE, INTEGRATION_STATUS, DISCLAIMER_TEXT)
VALUES (
    4, 'Tata 1mg', 'https://www.1mg.com/', 'https://www.1mg.com/search/all?name={query}',
    'Online Pharmacy', 1, 'External Link Verified',
    'External online healthcare platform. Genuine prescription verification managed by Tata 1mg.'
);

INSERT INTO PHARMACY_PROVIDERS (PROVIDER_ID, PROVIDER_NAME, BASE_URL, SEARCH_URL_TEMPLATE, CATEGORY_TAG, IS_ACTIVE, INTEGRATION_STATUS, DISCLAIMER_TEXT)
VALUES (
    5, 'Apollo Pharmacy', 'https://www.apollopharmacy.in/', 'https://www.apollopharmacy.in/search-medicines/{query}',
    'Retail & Online Pharmacy', 1, 'External Link Verified',
    'External certified retail pharmacy network. Prices and availability subject to store location.'
);

INSERT INTO PHARMACY_PROVIDERS (PROVIDER_ID, PROVIDER_NAME, BASE_URL, SEARCH_URL_TEMPLATE, CATEGORY_TAG, IS_ACTIVE, INTEGRATION_STATUS, DISCLAIMER_TEXT)
VALUES (
    6, 'PharmEasy', 'https://pharmeasy.in/online-medicine-order', 'https://pharmeasy.in/search/all?name={query}',
    'Online Pharmacy', 1, 'External Link Verified',
    'External platform link. Prescription required for Schedule H/X drugs.'
);

INSERT INTO PHARMACY_PROVIDERS (PROVIDER_ID, PROVIDER_NAME, BASE_URL, SEARCH_URL_TEMPLATE, CATEGORY_TAG, IS_ACTIVE, INTEGRATION_STATUS, DISCLAIMER_TEXT)
VALUES (
    7, 'Netmeds', 'https://www.netmeds.com/c/', 'https://www.netmeds.com/catalogsearch/result?q={query}',
    'Online Pharmacy', 1, 'External Link Verified',
    'External medicine store link. Subject to Netmeds terms and conditions.'
);

-- 13. MEDICINE REMINDERS
INSERT INTO MEDICINE_REMINDERS (REMINDER_ID, PATIENT_USER_ID, MEDICINE_NAME, DOSAGE, REMINDER_TIME, DAYS_OF_WEEK, START_DATE, IS_ACTIVE)
VALUES (1, 1, 'Vitamin D3', '60,000 IU', '09:00', 'Sunday', TO_DATE('2024-10-15', 'YYYY-MM-DD'), 1);

INSERT INTO MEDICINE_REMINDERS (REMINDER_ID, PATIENT_USER_ID, MEDICINE_NAME, DOSAGE, REMINDER_TIME, DAYS_OF_WEEK, START_DATE, IS_ACTIVE)
VALUES (2, 1, 'Cetirizine', '10 mg', '21:30', 'Daily', TO_DATE('2024-10-18', 'YYYY-MM-DD'), 1);

COMMIT;
