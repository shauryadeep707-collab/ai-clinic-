# Unified Patient Health Timeline Architecture

## Purpose
The **Unified Patient Health Timeline** is a central architectural feature of AI Health Clinic. It consolidates all fragmented medical interactions into a single chronological ledger so patients and authorized doctors never have to navigate multiple disjointed pages.

## Event Aggregation & Synchronization Strategy
The timeline uses an authoritative database ledger (`HEALTH_TIMELINE_EVENTS`) that is synchronized within transactions across the platform:
1. **Report Upload**: When a patient uploads a laboratory or imaging document, a `Report Upload` timeline event is automatically generated, linking to `MEDICAL_REPORTS`.
2. **AI Consultation**: Concluded triage sessions produce an `AI Consultation` event linking to `AI_CONSULTATIONS`.
3. **Doctor Consultations**: Scheduled or completed doctor appointments generate a `Doctor Consultation` event linking to `APPOINTMENTS`.
4. **Prescriptions**: Clinician issued medications generate a `Prescription` timeline event.
5. **Health Observations**: Self-recorded blood pressure or glucose logs generate a `Health Observation` event.

## Timeline Invariant Rules
- **No Fictional Events**: Failed uploads or incomplete consultations never produce timeline entries.
- **Accurate Medical Dates**: The timeline displays the actual date of the medical occurrence (`EVENT_DATE`), clearly distinguishing it from the `UPLOAD_DATE`.
- **Source Record Deep-Linking**: Every timeline card provides a direct link to the original report document, consultation dialogue, or doctor note.
- **Access Authorization**: The timeline endpoint strictly filters by authenticated `patient_user_id`. Unauthorized users cannot retrieve another patient's timeline events.
