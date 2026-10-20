# Automated Test Suite — AI Health Clinic

## Purpose
This directory contains the automated test suite testing security, authentication, medical report extraction, timeline synchronization, doctor verification, and clinical safety rules.

## Test Files
- `test_auth.py`: User registration, password verification with bcrypt, invalid credentials, duplicate email prevention, and JWT token issuance.
- `test_ai_safety.py`: Independent clinical emergency red-flag triggers (cardiac chest pain, FAST stroke symptoms, acute dyspnea, Hindi/Hinglish triggers) and cautious routine triage.
- `test_medical_reports.py`: Lab parameter extraction against reference ranges (Hemoglobin, Fasting Glucose, Vitamin D), report listing, and grounded summaries.
- `test_timeline.py`: Chronological ordering of health events, filtering by category, date range queries, and linked source record verification.
- `test_doctor_verification.py`: Verification queue retrieval, admin approval/rejection decisions, and status transitions.
- `test_pharmacy.py`: Verification of the 7 official Indian pharmacy destinations, query redirection, and patient-specific allergy alerts.
- `../c_modules/tests/test_c_metrics.py`: Clinical biometric index calculations (BMI, Mosteller BSA, CKD-EPI eGFR).

## How to Run Tests
```bash
python -m pytest -v
```
All tests are automated, repeatable, and run without requiring external network connectivity.
