# Frontend Documentation — AI Health Clinic

## Purpose
The `frontend/` directory contains the responsive, zero-framework HTML5, CSS3, and Vanilla JavaScript client interface for the AI Health Clinic web platform.

## Folder Structure
- `html/`: Webpages for public visitors, patients, doctors, and system administrators:
  - `index.html`: Public landing page matching Screen 1.
  - `patient-dashboard.html`: Patient dashboard with action cards, recent reports, and upcoming appointments (Screen 2).
  - `ai-consultation.html`: Multi-turn conversational AI consultation interface with summary panel and medical sources (Screen 3).
  - `medical-reports.html`: Medical reports table with category tabs and OCR upload modal (Screen 4).
  - `timeline.html`: Complete Medical History & Unified Health Timeline (Screen 5).
  - `doctors.html`: Find a Doctor directory with rating, verified badges, and appointment booking modal (Screen 6).
  - `doctor-register.html`: Doctor onboarding with multi-step progress and verification status tracker (Screen 7).
  - `doctor-dashboard.html`: Clinician practice overview with stats and today's appointments (Screen 8).
  - `admin-dashboard.html`: Doctor verification audit queue with approve/reject workflow (Screen 9).
  - `pharmacy-connect.html`: AI Medicine Guidance & 7 verified Indian pharmacy destinations.
  - `reminders.html`: Medicine schedule and adherence tracking.
  - `report-comparison.html`: Longitudinal lab value comparison across time.
  - `about.html`, `how-it-works.html`, `health-library.html`, `privacy.html`, `disclaimer.html`, `contact.html`, `login.html`, `register.html`, `reset-password.html`, `404.html`.
- `css/styles.css`: Complete medical design system adhering to colors: Navy `#15324B`, Teal `#0D9488`, Mint `#CCFBF1`, and Slate `#F1F5F9`.
- `js/api.js`: Unified HTTP client handling JWT bearer headers, error handling, and toast notifications.
- `js/auth.js`: Session handling, login, registration, and logout routines.

## How it Connects to the Backend
All interactive elements communicate with FastAPI backend endpoints (`/api/auth/*`, `/api/patients/*`, `/api/consultations/*`, `/api/medical-reports/*`, `/api/timeline/*`, `/api/doctors/*`, `/api/medicines/*`, `/api/pharmacies/*`, `/api/admin/*`) via the Fetch API in `frontend/js/api.js`.

## Common Issues & Solutions
- **401 Unauthorized**: User token has expired or is missing. The client will automatically clear `localStorage` and redirect to `login.html`.
- **CORS Issues**: Ensure the backend is running with CORS middleware enabled (enabled by default on all origins in development).
