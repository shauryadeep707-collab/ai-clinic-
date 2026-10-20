# Doctor Verification Architecture & Official Registry Integrations

## Purpose
To ensure that only legitimately licensed medical professionals provide medical advice and consultations on AI Health Clinic.

## Official Verification Starting Points
1. **Academic Qualification Depository**:
   - DigiLocker National Academic Depository (NAD): `https://nad.digilocker.gov.in/`
   - NAD Verifier Portal: `https://nad.digilocker.gov.in/Verifier`
   - Workflow: When API credentials and organization accreditation are active, automated queries verify degree authenticity directly with university repositories.
2. **Medical Registration Councils**:
   - National Medical Commission (NMC) Indian Medical Register: `https://www.nmc.org.in/information-desk/indian-medical-register/`
   - NMC Doctor Search: `https://nmr.nmc.org.in/search-doctor`
   - State Medical Councils (Delhi Medical Council, Maharashtra Medical Council, Karnataka Medical Council, etc.)

## Fallback & Review Protocol
- When automated API integrations are pending government accreditation, the system automatically routes applications to the Administrator Verification Queue for manual evidence auditing.
- Doctors remain in `Pending` status and cannot accept patient appointments until approved.
- AI never independently certifies a degree or approves a doctor. A human administrator conducts the final review.
