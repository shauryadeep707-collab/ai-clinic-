# Doctor Verification Subsystem — AI Health Clinic

## Purpose
The `doctor_verification/` directory implements the clinician onboarding, academic qualification check, and State Medical Council / NMC registration verification workflows.

## Verification Workflow
Doctors pass through a rigorous 5-stage onboarding workflow matching Image Screen 7:
1. **Personal Details**: Legal name, contact information, identity confirmation.
2. **Professional Details**: Specialization, medical council registration number, council name, years of experience.
3. **Upload Documents**: Medical degree certificate, state medical registration certificate, government ID.
4. **Verification Checks**:
   - **Academic Qualification**: Verified via the official DigiLocker / National Academic Depository (NAD) API (`https://nad.digilocker.gov.in/Verifier`) where authorized.
   - **Medical Registration**: Cross-referenced against the National Medical Commission (NMC) Indian Medical Register (`https://nmr.nmc.org.in/search-doctor`).
   - If external APIs are unconfigured or pending government accreditation, the system routes applications to the Administrator Review Queue for manual evidence auditing.
5. **Completed**: Approved doctors obtain the green `Verified` badge and can accept appointments.

## Verification Statuses
- `Submitted`
- `Pending`
- `Under review`
- `Additional info required`
- `Verified`
- `Rejected`
- `Suspended`
