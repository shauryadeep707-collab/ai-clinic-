# Database Design — AI Health Clinic

## Overview
AI Health Clinic employs a normalized relational schema compatible with Oracle Database (19c/21c/23c/Autonomous Database) and SQLite.

## Table Inventory
1. **USERS**: Core authentication identity (email, password hash, role: patient/doctor/admin, is_verified).
2. **PATIENT_PROFILES**: Medical demographics (blood group, date of birth, emergency contact, known allergies, chronic conditions).
3. **DOCTOR_PROFILES**: Clinical credentials (specialization, qualification summary, medical registration number, council name, consultation fee, verification status, rating).
4. **USER_CONSENTS**: Explicit legal and data processing consent records.
5. **RECORD_SHARING_PERMISSIONS**: Fine-grained patient-to-doctor permissions governing who can view reports and timeline data.
6. **DOCTOR_APPLICATIONS**: Application onboarding submissions.
7. **DOCTOR_QUALIFICATIONS**: Degrees, awarding universities, DigiLocker verification status.
8. **DOCTOR_REGISTRATIONS**: State Medical Council / NMC registration checks.
9. **DOCTOR_VERIFICATION_EVIDENCE**: Stored certificate documents and OCR audit text.
10. **DOCTOR_VERIFICATION_REVIEWS**: Administrator review decisions and audit trail.
11. **MEDICAL_REPORTS**: Patient test documents (test date, issue date, upload date, lab name, storage path, raw text).
12. **REPORT_SUMMARIES**: Grounded AI summaries, key findings, normal/abnormal highlights, and questions for doctor.
13. **REPORT_EXTRACTED_MEASUREMENTS**: Structured lab metrics (Hemoglobin, Fasting Glucose, Vitamin D, etc.) with clinical reference ranges.
14. **AI_CONSULTATIONS**: Symptom assessment sessions and triage levels (Emergency, Routine).
15. **AI_CONSULTATION_MESSAGES**: Dialogue message history between patient and assistant.
16. **APPOINTMENTS**: Consultation bookings with time slots and status.
17. **DOCTOR_AVAILABILITY**: Clinician working schedules and days of week.
18. **PATIENT_HEALTH_OBSERVATIONS**: Patient-recorded vitals (blood pressure, blood glucose).
19. **MEDICINES**: Drug reference catalog (indications, precautions, contraindications, side effects).
20. **PRESCRIPTIONS**: Clinician issued prescriptions.
21. **PRESCRIPTION_ITEMS**: Specific medication items per prescription.
22. **MEDICINE_REMINDERS**: Patient adherence reminder schedules.
23. **PHARMACY_PROVIDERS**: 7 official verified pharmacy destinations.
24. **HEALTH_TIMELINE_EVENTS**: Central chronological health journey ledger.
25. **AUDIT_LOGS**: Security and access logs.

## Date Separation Rule
The database strictly distinguishes:
- `EVENT_DATE`: The actual date the clinical event took place.
- `TEST_DATE`: The date a laboratory specimen was drawn.
- `REPORT_ISSUE_DATE`: The date the lab finalized the document.
- `UPLOAD_DATE`: The date the document was uploaded to the platform.
- `CREATED_AT`: The database row insertion timestamp.
