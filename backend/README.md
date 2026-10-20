# Backend Documentation — AI Health Clinic

## Purpose
The `backend/` directory houses the core Python FastAPI web application, database layer (Oracle Database & SQLite), business logic services, schemas, and security infrastructure.

## Folder Structure
- `app/main.py`: Primary FastAPI application entrypoint, CORS configuration, static asset mounting, and lifespan startup initialization.
- `app/config/settings.py`: Environment configuration loading from `.env` (Oracle credentials, JWT keys, AI provider mode).
- `app/database/connection.py`: Database engine supporting Oracle Database (via `oracledb`) and SQLite (`ai_health_clinic.db`) with automatic table creation and synthetic data seeding.
- `app/security/auth.py`: Password hashing using `bcrypt`, JWT token issuance and decoding using `PyJWT`, role-based access control (`require_role`), and patient record isolation.
- `app/schemas/`: Pydantic validation schemas for authentication, reports, consultations, appointments, and medicine lookups.
- `app/services/`:
  - `timeline_service.py`: Central ledger synchronization for medical reports, consultations, doctor notes, and appointments.
  - `report_service.py`: Secure file storage, text extraction (via `pypdf` and `Pillow`), and grounded AI report summarization.
  - `doctor_service.py`: Doctor verification workflow, dashboard metrics, and review queue.
  - `appointment_service.py`: Booking conflict prevention and timeline synchronization.
  - `medicine_service.py`: Educational medicine catalog, patient allergy warnings, and verified pharmacy search links.
- `app/routers/`: Modular API route controllers (`auth.py`, `patients.py`, `consultations.py`, `medical_reports.py`, `timeline.py`, `doctors.py`, `appointments.py`, `medicines.py`, `pharmacies.py`, `admin.py`).
- `uploads/`: Private directories for patient medical reports and doctor credentials.

## How to Run
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation is available at:
`http://localhost:8000/docs`
