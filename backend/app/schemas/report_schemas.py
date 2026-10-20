from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MeasurementItem(BaseModel):
    test_metric_name: str
    observed_value: float
    unit: str
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    status_flag: str = "Normal"
    notes: Optional[str] = None

class ReportSummaryResponse(BaseModel):
    summary_id: int
    report_id: int
    ai_summary_text: str
    key_findings: Optional[str] = None
    normal_metrics: Optional[str] = None
    abnormal_metrics: Optional[str] = None
    questions_for_doctor: Optional[str] = None
    source_grounding_disclaimer: str

class ReportResponse(BaseModel):
    report_id: int
    patient_user_id: int
    report_title: str
    report_category: str
    test_name: Optional[str] = None
    test_date: Optional[str] = None
    report_issue_date: Optional[str] = None
    upload_date: str
    issuing_lab_or_hospital: Optional[str] = None
    file_name: str
    file_size_bytes: int
    file_mime_type: str
    processing_status: str
    extracted_raw_text: Optional[str] = None
    doctor_interpretation: Optional[str] = None
    doctor_follow_up_notes: Optional[str] = None
    ai_summary: Optional[ReportSummaryResponse] = None
    measurements: List[MeasurementItem] = []

class ReportComparisonItem(BaseModel):
    test_metric_name: str
    unit: str
    values_by_date: List[Dict[str, Any]] # [{"test_date": "2024-10-15", "value": 14.2, "status": "Normal"}]
