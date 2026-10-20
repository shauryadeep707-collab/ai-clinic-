# System Architecture — AI Health Clinic

## High-Level Architecture Overview

```mermaid
flowchart TD
    Client["Responsive Web Frontend (HTML5 / CSS3 / Vanilla JS)"]
    
    subgraph Gateway ["Application Gateway & Security"]
        AuthLayer["Authentication & RBAC (JWT + Bcrypt)"]
        Validation["Pydantic Request/Response Validation"]
    end
    
    subgraph CoreBackend ["FastAPI Core Backend"]
        AuthRouter["Auth Router (/api/auth)"]
        PatientRouter["Patient Router (/api/patients)"]
        ConsultRouter["Consultation Router (/api/consultations)"]
        ReportRouter["Medical Reports Router (/api/medical-reports)"]
        TimelineRouter["Timeline Router (/api/timeline)"]
        DoctorRouter["Doctor Router (/api/doctors)"]
        ApptRouter["Appointments Router (/api/appointments)"]
        MedicineRouter["Medicine & Reminders (/api/medicines)"]
        PharmacyRouter["Pharmacy Connect (/api/pharmacies)"]
        AdminRouter["Admin Router (/api/admin)"]
    end

    subgraph AISubsystem ["AI Engine & Safety Rule Layer"]
        EmergencyTriage["Clinical Red-Flag Emergency Rules"]
        Grounding["Report Value Grounding & Summarizer"]
        SourceRetrieval["Medical Reference Library (NHS / Mayo / WHO)"]
    end

    subgraph StorageLayer ["Data & Storage Layer"]
        DBManager["Database Engine (Oracle Database / SQLite)"]
        PrivateFS["Private Encrypted File Storage (Uploads)"]
    end

    subgraph ExternalServices ["External Healthcare Ecosystem"]
        DigiLocker["DigiLocker / NAD Academic Repository"]
        NMC["NMC Indian Medical Register"]
        Pharmacies["Verified Official Pharmacies (7 Destinations)"]
    end

    Client --> AuthLayer --> Validation --> CoreBackend
    ConsultRouter --> AISubsystem
    ReportRouter --> AISubsystem
    CoreBackend --> DBManager
    ReportRouter --> PrivateFS
    DoctorRouter -.-> DigiLocker
    DoctorRouter -.-> NMC
    PharmacyRouter -.-> Pharmacies
```

## Architectural Principles
1. **Clinical Safety Decoupled from LLM**: Emergency signs (e.g. chest pain, stroke symptoms) are identified deterministically by the rule layer before any language model generation.
2. **Authoritative Timeline Synchronization**: The Unified Health Timeline is automatically synchronized when reports are uploaded, consultations concluded, or appointments scheduled.
3. **Multi-Tenant Data Isolation**: Patient medical records can never be traversed or accessed by altering URL IDs.
4. **Dual Database Adaptability**: Production deployments connect to Oracle Database (via `oracledb`) using parameterized queries; local development defaults to SQLite (`ai_health_clinic.db`) with zero manual setup.
