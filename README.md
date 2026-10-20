# AI Health Clinic
### Complete Full-Stack Healthcare Platform with AI, Medical History, Unified Timeline, Doctor Verification, and Pharmacy Integration

[![Tests](https://img.shields.io/badge/pytest-20%20passed%20(100%25)-success)](https://github.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-Oracle%20%26%20SQLite-F80000)](https://www.oracle.com/database/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. Project Overview
**AI Health Clinic** is a full-stack healthcare web application that connects patients, cautious AI-powered health guidance, medical report management, verified clinicians, appointment bookings, medicine safety information, and external official pharmacy channels.

The platform provides a modern medical interface (Navy `#15324B`, Medical Teal `#0D9488`, Mint `#CCFBF1`, and Slate `#F1F5F9`) with role-based access for:
- **Patients**: Consult AI assistant, upload medical reports, read AI explanations, access the Unified Patient Health Timeline, maintain a complete medical history, compare lab metrics over time, book appointments with verified doctors, track medicine reminders, and find verified medicines across 7 official Indian pharmacy destinations.
- **Doctors**: Register, submit qualifications/certificates for verification, manage availability, view appointments, review authorized patient records and AI report summaries, and manage consultation history.
- **Administrators**: Review doctor credential applications (DigiLocker/NAD and State Medical Council checks), approve or reject applications, audit security logs, and monitor system metrics.

---

## 2. Technologies Used
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+), Fetch API. Responsive desktop sidebar and mobile navigation.
- **Backend**: Python 3.12+, FastAPI, Pydantic, Starlette, Uvicorn.
- **Database**:
  - **Oracle Database**: Production DDL scripts (`01_create_tables.sql`, `02_constraints_and_indexes.sql`, `03_seed_test_data.sql`, `04_sample_queries.sql`, `05_cleanup_test_data.sql`) compatible with Oracle 19c/21c/23c and Oracle Live SQL via Python `oracledb`.
  - **SQLite Engine**: Automatic zero-setup development engine (`ai_health_clinic.db`) with identical schema and pre-seeded demonstration data.
- **AI & Document Processing**:
  - Independent clinical emergency rule triage layer (cardiac, stroke FAST, dyspnea, anaphylaxis).
  - Grounded lab summarizer for CBC, fasting glucose, vitamin D, and renal profiles.
  - PDF & image processing via `pypdf` and `Pillow`.
- **High-Performance C Module**: High-precision biometric and dosage calculations (BMI, Mosteller BSA, CKD-EPI eGFR, Clark's pediatric dosage) with Python `ctypes` wrapper in `c_modules/`.
- **Security & Testing**: Bcrypt password hashing, PyJWT authentication tokens, role-based access control, parameterized SQL queries, and automated testing with `pytest`.

---

## 3. Project Structure
```text
ai-health-clinic/
├── frontend/
│   ├── html/
│   │   ├── index.html                   # Public Homepage (Screen 1)
│   │   ├── patient-dashboard.html       # Patient Dashboard (Screen 2)
│   │   ├── ai-consultation.html         # AI Consultation & Summary Panel (Screen 3)
│   │   ├── medical-reports.html         # Medical Reports & OCR Upload (Screen 4)
│   │   ├── timeline.html                # Unified Health Timeline & History (Screen 5)
│   │   ├── doctors.html                 # Find a Doctor & Booking (Screen 6)
│   │   ├── doctor-register.html         # Doctor Registration & Verification Flow (Screen 7)
│   │   ├── doctor-dashboard.html        # Doctor Dashboard & Appointments (Screen 8)
│   │   ├── admin-dashboard.html         # Admin Verification Queue (Screen 9)
│   │   ├── pharmacy-connect.html        # AI Medicine Guidance & Pharmacy Connect
│   │   ├── reminders.html               # Medicine Reminders
│   │   ├── report-comparison.html       # Longitudinal Lab Report Comparison
│   │   ├── about.html, how-it-works.html, health-library.html, settings.html, privacy.html, disclaimer.html, contact.html, reset-password.html, 404.html
│   ├── css/styles.css                   # Complete Medical Design System
│   ├── js/
│   │   ├── api.js                       # Centralized API fetch wrapper with JWT
│   │   └── auth.js                      # Login, registration, and session routines
│   └── README.md
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI application entrypoint
│   │   ├── config/settings.py           # Environment settings
│   │   ├── database/connection.py       # Oracle & SQLite database manager & seeder
│   │   ├── security/auth.py             # Bcrypt hashing, JWT tokens, RBAC, isolation
│   │   ├── schemas/                     # Pydantic request/response models
│   │   ├── services/                    # Timeline, reports, doctor, appointment, medicine services
│   │   └── routers/                     # 10 API route controllers
│   ├── uploads/                         # Private document storage
│   ├── requirements.txt
│   └── README.md
├── ai/
│   ├── safety_rules/emergency_rules.py  # Emergency red-flag detection layer
│   ├── health_assistant/assistant.py    # Multi-turn consultation engine (EN, HI, Hinglish)
│   ├── medical_retrieval/sources.py     # Verified NHS, Mayo Clinic, WHO guidelines
│   ├── report_summarization/summarizer.py# Grounded lab metric parser
│   └── README.md
├── doctor_verification/
│   └── README.md                        # DigiLocker / NAD & NMC verification workflow
├── pharmacy_connect/
│   └── README.md                        # 7 verified official Indian pharmacy destinations
├── c_modules/
│   ├── include/medical_metrics.h        # C header
│   ├── src/medical_metrics.c            # C implementation
│   ├── wrapper.py                       # Python ctypes binding with fallback
│   ├── tests/test_c_metrics.py
│   └── README.md
├── database/
│   ├── sql/                             # Complete Oracle DDL/DML scripts
│   ├── diagrams/er_diagram.md           # Mermaid ER diagram
│   └── README.md
├── tests/                               # 20 Automated pytest test cases (100% passing)
├── docs/                                # Architecture, API docs, workflows, troubleshooting
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 4. Quick Start & Installation

### Step 1: Clone & Environment Setup
Ensure Python 3.10+ is installed:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*Note: By default, `DB_ENGINE=sqlite` is configured, which creates and seeds `ai_health_clinic.db` automatically with zero manual setup.*

### Step 4: Start the Full-Stack Server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
- **Web Application**: `http://localhost:8000/` or `http://localhost:8000/static/html/index.html`
- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`

---

## 5. Demonstration Accounts (Pre-Seeded)
The application comes pre-loaded with realistic synthetic test data matching all UI screens:

| Role | Email | Password | Full Name | Access Capabilities |
|---|---|---|---|---|
| **Patient** | `patient@clinic.com` | `Password@123` | Rohan Sharma | Consult AI, view reports, unified timeline, book doctors |
| **Doctor** | `doctor@clinic.com` | `Password@123` | Dr. Amit Verma | Practice overview, appointments, patient reports |
| **Doctor** | `dr.priya@clinic.com`| `Password@123` | Dr. Priya Mehta | Cardiologist profile, appointment schedule |
| **Administrator** | `admin@clinic.com` | `Password@123` | System Administrator | Review doctor applications queue, audit logs, system stats |

---

## 6. Oracle Database Configuration
To connect to an Oracle Database instance (Oracle Cloud Autonomous Database, Oracle XE, or Oracle Live SQL):
1. Execute the SQL scripts in `database/sql/` in order:
   - `01_create_tables.sql`
   - `02_constraints_and_indexes.sql`
   - `03_seed_test_data.sql`
2. Update `.env`:
   ```env
   DB_ENGINE=oracle
   ORACLE_USER=admin
   ORACLE_PASSWORD=YourPassword
   ORACLE_DSN=localhost:1521/XEPDB1
   ```

---

## 7. Running Automated Tests
Run the comprehensive automated test suite with pytest:
```bash
python -m pytest -v
```
All 20 tests verify:
- Patient/Doctor/Admin authentication & registration isolation.
- Emergency red-flag safety triggers (cardiac, stroke, dyspnea, Hindi/Hinglish).
- Medical report parsing against reference ranges (Hemoglobin, Fasting Sugar, Vitamin D).
- Unified timeline chronological ordering & source linking.
- Doctor verification admin approval/rejection workflows.
- Patient allergy cross-referencing (Penicillin allergy alert for Amoxicillin).
- Official external pharmacy destinations.
- High-performance C biometric calculations (BMI, BSA, eGFR).

---

## 8. Clinical Safety & Known Limitations
- **Educational Tool Only**: The AI Health Assistant does not possess a medical license and cannot replace a doctor.
- **No Independent Prescribing**: The system will never independently prescribe antibiotics or Schedule H drugs.
- **Government APIs**: Official DigiLocker/NAD and NMC Indian Medical Register production APIs require institutional government accreditation; pending approval, applications are audited in the manual verification queue.
- **External Pharmacies**: The 7 official pharmacy destinations are external starting links; real-time pricing and stock must be confirmed on the external provider's platform.
