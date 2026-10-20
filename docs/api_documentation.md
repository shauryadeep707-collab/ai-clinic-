# API Reference — AI Health Clinic

The application provides a comprehensive RESTful API built with FastAPI. Interactive documentation and OpenAPI specifications are available at `http://localhost:8000/docs`.

## 1. Authentication (`/api/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new Patient or Doctor account |
| `POST` | `/api/auth/login` | Authenticate with email/password, returns JWT token |
| `GET` | `/api/auth/me` | Fetch currently authenticated user profile |
| `POST` | `/api/auth/logout` | Session teardown |
| `POST` | `/api/auth/reset-password` | Update account password |

## 2. Patient Profiles (`/api/patients`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/patients/profile` | Retrieve personal & medical details |
| `PUT` | `/api/patients/profile` | Update medical profile, allergies, and emergency contact |
| `GET` | `/api/patients/dashboard-summary` | Summary metrics for Patient Dashboard (recent reports, upcoming appts) |
| `POST` | `/api/patients/observations` | Record self-logged health observation (blood pressure, glucose, vitals) |
| `GET` | `/api/patients/observations` | List recorded observations |

## 3. AI Health Assistant (`/api/consultations`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/consultations` | Start new AI consultation session |
| `GET` | `/api/consultations` | List patient's past consultation history |
| `GET` | `/api/consultations/{id}` | Retrieve specific consultation session with message stream |
| `POST` | `/api/consultations/{id}/messages` | Post patient symptom message, trigger clinical safety check & AI guidance |

## 4. Medical Reports (`/api/medical-reports`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/medical-reports/upload` | Multipart upload (PDF/images), runs OCR & AI summarization, syncs to timeline |
| `GET` | `/api/medical-reports` | List patient reports with category filter (`Blood Tests`, `Imaging`, `Prescriptions`, `Other`) |
| `GET` | `/api/medical-reports/{id}` | Detailed report view with AI summary and extracted lab metrics |
| `GET` | `/api/medical-reports/{id}/download` | Stream authentic stored original file |
| `GET` | `/api/medical-reports/comparison` | Longitudinal comparison of blood metrics over time |

## 5. Unified Health Timeline (`/api/timeline`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/timeline` | Retrieve chronological timeline events with category filter, search, date range, and pagination |
| `GET` | `/api/timeline/{id}` | Retrieve event details with linked source document |

## 6. Doctors & Verification (`/api/doctors`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/doctors` | List verified clinicians with specialization filter |
| `GET` | `/api/doctors/{id}` | Retrieve doctor credentials, council details, and rating |
| `POST` | `/api/doctors/applications` | Submit doctor credentials and certificates for verification |
| `GET` | `/api/doctors/dashboard/stats` | Clinician dashboard metrics (today's appointments, patients, pending reports) |

## 7. Appointments (`/api/appointments`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/appointments` | List appointments for logged-in patient or doctor |
| `POST` | `/api/appointments` | Book appointment with conflict checking and timeline sync |
| `PUT` | `/api/appointments/{id}/cancel` | Cancel appointment |
| `PUT` | `/api/appointments/{id}/complete` | Mark completed with clinical notes |

## 8. Medicines & Pharmacy Connect (`/api/medicines`, `/api/pharmacies`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/medicines` | Search educational medicine catalog |
| `GET` | `/api/medicines/{id}` | View indications, contraindications, and precautions |
| `POST` | `/api/medicines/allergy-check` | Check candidate medicine against patient's documented allergies |
| `GET` | `/api/medicines/reminders` | Active medicine schedule reminders |
| `POST` | `/api/medicines/reminders` | Create reminder |
| `GET` | `/api/pharmacies` | List 7 official Indian pharmacy destinations |
| `GET` | `/api/pharmacies/search` | Search verified pharmacy destination landing URLs |

## 9. Administrator (`/api/admin`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/doctors/verification-queue` | Doctor onboarding review queue |
| `POST` | `/api/admin/doctors/review` | Approve, reject, or request additional evidence |
| `GET` | `/api/admin/stats` | System metrics (total users, verified doctors, reports processed) |
| `GET` | `/api/admin/audit-logs` | Access audit trail |
