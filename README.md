# AI Health Clinic & Assistant (Integrated Full-Stack Project)

This project combines:
1. **Frontend**: The complete medical design system, responsive UI, patient & doctor portals, and 23 interactive screens from the **`clinic`** project.
2. **Backend**: The robust, multi-database architecture (Flask, Supabase PostgreSQL, SQLite, NLP symptom triage, deterministic risk engine, doctor routing, and pharmacy connect) from **`bestproject`**.

---

## 1. Quick Start

### Windows (One-Click)
Run `start.bat` or open PowerShell in this directory:
```powershell
python run.py
```
Open **`http://localhost:5000`** in your web browser.

---

## 2. Demo User Accounts

| Role | Email | Password | Full Name & Details |
| :--- | :--- | :--- | :--- |
| **Patient (Clinic)** | `patient@clinic.com` | `Password@123` | Rohan Sharma (Age 28, Male) |
| **Doctor (Clinic)** | `doctor@clinic.com` | `Password@123` | Dr. Amit Verma (General Physician) |
| **Doctor (Specialist)** | `dr.priya@clinic.com` | `Password@123` | Dr. Priya Mehta (Cardiologist) |
| **Administrator** | `admin@clinic.com` | `Password@123` | System Administrator |
| **Patient (Demo)** | `patient@demo.com` | `Patient@123` | Rahul Sharma (Age 28, Male) |
| **Doctor (Demo)** | `doctor@demo.com` | `Doctor@123` | Dr. Amit Verma (Dehradun Practice) |
| **Admin (Demo)** | `admin@demo.com` | `Admin@123` | Admin User |

> **Tip**: On the Login screen (`/static/html/login.html`), you can click any of the **Quick-Fill Preset Account Pills** to autofill credentials and sign in instantly.

---

## 3. Project Architecture

```text
mix of the ai/
├── frontend/                     # Modern Navy & Teal Medical Interface (from clinic)
│   ├── html/
│   │   ├── index.html            # Public Landing Page (Screen 1)
│   │   ├── login.html            # Role-Based Login & Quick-Fill
│   │   ├── register.html         # Patient Sign Up
│   │   ├── patient-dashboard.html# Patient Portal Dashboard (Screen 2)
│   │   ├── ai-consultation.html  # AI Symptom Consultation & Clinical Triage (Screen 3)
│   │   ├── medical-reports.html  # Lab Reports, OCR & Grounded Explanations (Screen 4)
│   │   ├── timeline.html         # Unified Longitudinal Medical Journey (Screen 5)
│   │   ├── doctors.html          # Find Verified Doctors & Book Slots (Screen 6)
│   │   ├── doctor-register.html  # Doctor Application & Verification (Screen 7)
│   │   ├── doctor-dashboard.html # Doctor Queue & Patient Records (Screen 8)
│   │   ├── admin-dashboard.html  # Administrator Verification Queue (Screen 9)
│   │   ├── pharmacy-connect.html # Drug Guidance & 7 External Pharmacy Links
│   │   ├── reminders.html        # Medicine Adherence Reminders
│   │   ├── report-comparison.html# Metric Progression Comparison
│   │   └── ... (about, health-library, settings, 404, etc.)
│   ├── css/styles.css            # Medical Design System (Teal, Navy, Mint, Slate)
│   └── js/
│       ├── api.js                # Centralized Fetch wrapper with Bearer JWT
│       └── auth.js               # Cross-portal session & identity manager
├── backend/                      # Python Flask Backend (from bestproject)
│   ├── app.py                    # Application factory, CSRF bypass, static mount
│   ├── config.py                 # Configuration module (.env loader)
│   ├── db.py                     # Unified DB layer (PostgreSQL + SQLite fallback)
│   ├── auth_utils.py             # RBAC, rate-limiting & JWT Bearer decoder
│   ├── routes/
│   │   ├── auth.py               # Authentication, registration, password reset
│   │   ├── patients.py           # Patient dashboard summary & profile
│   │   ├── consultations.py      # AI Consultation engine & doctor triage
│   │   ├── reports.py            # Report upload, OCR & lab metric parser
│   │   ├── timeline.py           # Longitudinal health timeline events
│   │   ├── appointments.py       # Doctor catalog, appointments & admin review
│   │   ├── pharmacies.py         # Multi-pharmacy search & allergy safety check
│   │   ├── doctors.py            # Nearby doctor discovery (Haversine formula)
│   │   ├── assessments.py        # Structured symptom checker
│   │   ├── notifications.py      # In-app notifications
│   │   └── health.py             # Health check endpoint
│   ├── services/
│   │   ├── ai_service.py         # Conversational NLP & multi-turn triage
│   │   ├── risk_engine.py        # Deterministic risk engine & red-flag detection
│   │   ├── summary_service.py    # Clinical briefing summary generator
│   │   ├── location_service.py   # Distance calculation for nearby doctors
│   │   └── knowledge_base.py     # Medical conditions & medicines catalog
│   └── uploads/                  # Uploaded diagnostic reports & doctor docs
├── ai/
│   ├── report_summarization/     # Grounded lab metric parser (CBC, Glucose, Vit D)
│   ├── medical_retrieval/        # NHS, Mayo Clinic & WHO guidelines retrieval
│   └── safety_rules/             # Emergency rule triage definitions
├── database/
│   ├── schema.postgres.sql       # Supabase PostgreSQL schema
│   ├── schema.sqlite.sql         # Local SQLite schema
│   ├── init_all_tables.py        # Automatic schema creator
│   └── seed_clinic_data.py       # Seed script for users, reports, timeline, pharmacies
├── knowledge_base/               # 77+ medicines, symptoms, and red flag datasets
├── run.py                        # Main entry point: python run.py
├── test_mix_app.py               # 15 automated integration tests (100% passing)
└── requirements.txt
```

---

## 4. Key Integrated Features

1. **AI Health Consultation & Clinical Triage**:
   - Chat interface in English, Hindi, and Hinglish.
   - Deterministic clinical red-flag engine (detects acute cardiac, stroke, dyspnea, anaphylaxis warnings and triggers emergency alerts).
   - Evidence-based guidance grounded in NHS, Mayo Clinic, and WHO sources.
2. **Medical Reports & OCR Parsing**:
   - Upload PDF and image diagnostic reports.
   - Extracts lab metrics (Hemoglobin, WBC, Platelets, Fasting Blood Sugar, Vitamin D, Creatinine) and checks against physiological reference ranges.
3. **Unified Health Timeline**:
   - Chronological patient health ledger aggregating lab reports, AI consultations, doctor visits, and medications.
4. **Verified Doctor Discovery & Booking**:
   - Find verified specialists (General Physician, Cardiologist, ENT, Pulmonologist, etc.).
   - Haversine distance-based discovery and online appointment booking.
5. **Pharmacy Connect & Drug-Allergy Safety**:
   - Live query links to 7 verified Indian pharmacy destinations (Apollo Pharmacy, Tata 1mg, Netmeds, PharmEasy, Blinkit, Swiggy Instamart, Amazon Pharmacy).
   - Drug-allergy cross-sensitivity check (e.g., Penicillin to Amoxicillin).
6. **Medicine Adherence Reminders**:
   - Schedule daily/weekly dosages and track completion.
7. **Doctor Credential Verification & Admin Audit**:
   - Onboarding flow for medical degrees and registration numbers with administrator review queue.

---

## 5. Running the Tests

To verify all 15 integration tests:
```powershell
python test_mix_app.py
```
Expected output:
```
ALL 15 INTEGRATION TESTS PASSED 100%!
```
