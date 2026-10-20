import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from pypdf import PdfReader
from PIL import Image

from backend.app.config.settings import settings
from backend.app.database.connection import get_db
from ai.report_summarization.summarizer import extract_and_summarize_report
from backend.app.services.timeline_service import timeline_service

logger = logging.getLogger("ai_health_clinic.reports")

class ReportService:
    @staticmethod
    def extract_text_from_file(file_path: Path, mime_type: str) -> str:
        extracted_text = ""
        try:
            if "pdf" in mime_type or file_path.suffix.lower() == ".pdf":
                reader = PdfReader(str(file_path))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            elif "image" in mime_type or file_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                # Open with Pillow to verify image validity
                with Image.open(file_path) as img:
                    img.verify()
                extracted_text = f"Scanned Medical Image: {file_path.name}. Image dimensions verified."
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            extracted_text = f"Text extraction warning: File content could not be fully parsed ({e})."
        
        return extracted_text.strip()

    @staticmethod
    def save_and_process_report(
        patient_user_id: int,
        file_obj,
        original_filename: str,
        report_title: str,
        report_category: str = "Other",
        test_date: Optional[str] = None,
        issuing_lab: Optional[str] = None,
        custom_raw_text: Optional[str] = None
    ) -> Dict[str, Any]:
        db = get_db()
        timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"pat{patient_user_id}_{timestamp_prefix}_{original_filename.replace(' ', '_')}"
        destination_path = settings.REPORTS_DIR / safe_filename

        # Write file to private storage
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)

        file_size = destination_path.stat().st_size
        mime_type = "application/pdf" if original_filename.lower().endswith(".pdf") else "image/jpeg"

        # Extract text
        if custom_raw_text:
            extracted_text = custom_raw_text
        else:
            extracted_text = ReportService.extract_text_from_file(destination_path, mime_type)
            if not extracted_text:
                extracted_text = f"Report: {report_title}. No raw text could be automatically extracted from scan."

        # Insert Medical Report
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        effective_test_date = test_date if test_date else current_date_str

        report_id = db.execute_write("""
            INSERT INTO medical_reports 
            (patient_user_id, report_title, report_category, test_name, test_date, report_issue_date, issuing_lab_or_hospital, file_name, file_storage_path, file_size_bytes, file_mime_type, processing_status, extracted_raw_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_user_id, report_title, report_category, report_title,
            effective_test_date, effective_test_date, issuing_lab or "Private Diagnostic Center",
            safe_filename, str(destination_path), file_size, mime_type, "Completed", extracted_text
        ))

        # AI Grounded Summarization & Metric Extraction
        ai_result = extract_and_summarize_report(extracted_text, report_title)

        # Save AI Summary
        db.execute_write("""
            INSERT INTO report_summaries 
            (report_id, ai_summary_text, key_findings, normal_metrics, abnormal_metrics, questions_for_doctor, source_grounding_disclaimer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            ai_result["ai_summary_text"],
            ai_result["key_findings"],
            ai_result["normal_metrics"],
            ai_result["abnormal_metrics"],
            ai_result["questions_for_doctor"],
            ai_result["source_grounding_disclaimer"]
        ))

        # Save Extracted Measurements
        for m in ai_result["extracted_measurements"]:
            db.execute_write("""
                INSERT INTO report_extracted_measurements
                (report_id, test_metric_name, observed_value, unit, reference_range_low, reference_range_high, status_flag, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id, m["test_metric_name"], m["observed_value"], m["unit"],
                m["reference_range_low"], m["reference_range_high"], m["status_flag"], m["notes"]
            ))

        # Automatically propagate to Unified Health Timeline
        short_desc = f"{report_category}: {ai_result['key_findings'][:100]}"
        timeline_service.add_timeline_event(
            patient_user_id=patient_user_id,
            event_type="Report Upload",
            event_title=report_title,
            event_date=effective_test_date,
            event_time=datetime.now().strftime("%I:%M %p"),
            short_description=short_desc,
            organization_or_doctor=issuing_lab or "Diagnostic Lab",
            record_reference_id=report_id,
            status_badge="Completed"
        )

        return ReportService.get_report_details(report_id)

    @staticmethod
    def get_report_details(report_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        report = db.query_one("SELECT * FROM medical_reports WHERE report_id = ?", (report_id,))
        if not report:
            return None
        report["ai_summary"] = db.query_one("SELECT * FROM report_summaries WHERE report_id = ?", (report_id,))
        report["measurements"] = db.query_all("SELECT * FROM report_extracted_measurements WHERE report_id = ?", (report_id,))
        return report

    @staticmethod
    def list_patient_reports(patient_user_id: int, category: Optional[str] = None) -> List[Dict[str, Any]]:
        db = get_db()
        if category and category.lower() != "all":
            reports = db.query_all("""
                SELECT * FROM medical_reports 
                WHERE patient_user_id = ? AND report_category = ?
                ORDER BY test_date DESC, report_id DESC
            """, (patient_user_id, category))
        else:
            reports = db.query_all("""
                SELECT * FROM medical_reports 
                WHERE patient_user_id = ?
                ORDER BY test_date DESC, report_id DESC
            """, (patient_user_id,))
        
        for r in reports:
            r["ai_summary"] = db.query_one("SELECT * FROM report_summaries WHERE report_id = ?", (r["report_id"],))
            r["measurements"] = db.query_all("SELECT * FROM report_extracted_measurements WHERE report_id = ?", (r["report_id"],))
        return reports

    @staticmethod
    def get_comparison_data(patient_user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all metrics tracked across multiple dates for report comparison.
        """
        db = get_db()
        sql = """
            SELECT m.test_metric_name, m.unit, m.observed_value, m.status_flag, r.test_date, r.report_title
            FROM report_extracted_measurements m
            JOIN medical_reports r ON m.report_id = r.report_id
            WHERE r.patient_user_id = ?
            ORDER BY m.test_metric_name, r.test_date ASC
        """
        rows = db.query_all(sql, (patient_user_id,))
        grouped: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            metric = row["test_metric_name"]
            if metric not in grouped:
                grouped[metric] = {
                    "test_metric_name": metric,
                    "unit": row["unit"],
                    "history": []
                }
            grouped[metric]["history"].append({
                "test_date": row["test_date"],
                "value": row["observed_value"],
                "status": row["status_flag"],
                "report_title": row["report_title"]
            })
        return list(grouped.values())

report_service = ReportService()
