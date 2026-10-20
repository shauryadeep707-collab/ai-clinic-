# Medical Reports & Complete Medical History Workflow

## Workflow Overview
1. **Document Upload**:
   - Patient uploads PDF, JPG, or PNG.
   - Validation checks file extension, MIME type, and size (max 15MB).
   - Stored in private directory `backend/uploads/reports/`.
2. **Data Extraction**:
   - `pypdf` extracts raw text from PDF documents.
   - `Pillow` verifies image integrity.
3. **Clinical Lab Value Parsing**:
   - Deterministic regex patterns identify Hemoglobin, Platelets, Total WBC, Fasting Glucose, Vitamin D, and Creatinine.
   - Compares observed values against standard adult reference ranges.
4. **Grounded AI Summarization**:
   - Formulates plain-English explanation grounded strictly in the observed numbers.
   - Generates questions for the doctor.
5. **Timeline Synchronization**:
   - Generates an entry in `HEALTH_TIMELINE_EVENTS`.
6. **Historical Preservation**:
   - Older reports are never overwritten. Every test is stored as a distinct record, enabling longitudinal comparison over time.
