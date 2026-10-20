# Troubleshooting Guide — AI Health Clinic

## 1. Application Startup Errors
- **Error: `ModuleNotFoundError`**:
  Ensure dependencies are installed:
  ```bash
  pip install -r backend/requirements.txt
  ```
- **Error: `email-validator`**:
  Standard Pydantic models in this codebase use robust string format validation to avoid third-party email validator dependency conflicts.

## 2. Database Connection Issues
- **Oracle Database Not Available**:
  By default, `DB_ENGINE=sqlite` is configured in `.env`, using local `ai_health_clinic.db` for instant zero-dependency execution.
  To connect to Oracle, set `DB_ENGINE=oracle` and configure `ORACLE_USER`, `ORACLE_PASSWORD`, and `ORACLE_DSN`.

## 3. Upload Failures
- **Error: File type not supported**:
  The system strictly accepts `.pdf`, `.png`, `.jpg`, and `.jpeg` under 15MB.
- **Empty Raw Text Extraction**:
  If an uploaded scan is unreadable or heavily blurred, the system notes the extraction warning and provides an input area to paste report values directly.

## 4. Port Conflicts
If port 8000 is occupied:
```bash
uvicorn backend.app.main:app --port 8080 --reload
```
