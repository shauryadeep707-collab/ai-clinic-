from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
from pathlib import Path
from backend.app.database.connection import get_db
from backend.app.security.auth import get_current_user, verify_patient_access
from backend.app.services.report_service import report_service

router = APIRouter(prefix="/api/medical-reports", tags=["Medical Reports"])

@router.post("/upload")
async def upload_report(
    report_title: str = Form(...),
    report_category: str = Form("Other"),
    test_date: Optional[str] = Form(None),
    issuing_lab: Optional[str] = Form(None),
    custom_raw_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    filename = file.filename if file else f"{report_title.replace(' ', '_')}.pdf"
    
    # If no file object is provided (e.g. text report entry), create virtual stream
    import io
    if file:
        file_obj = file.file
    else:
        dummy_content = (custom_raw_text or f"Medical Report: {report_title}").encode("utf-8")
        file_obj = io.BytesIO(dummy_content)

    processed_report = report_service.save_and_process_report(
        patient_user_id=user_id,
        file_obj=file_obj,
        original_filename=filename,
        report_title=report_title,
        report_category=report_category,
        test_date=test_date,
        issuing_lab=issuing_lab,
        custom_raw_text=custom_raw_text
    )

    return processed_report

@router.get("")
def list_reports(
    category: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    return report_service.list_patient_reports(user_id, category)

@router.get("/comparison")
def get_report_comparison(current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["user_id"]
    return report_service.get_comparison_data(user_id)

@router.get("/{report_id}")
def get_report(report_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    report = report_service.get_report_details(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Medical report not found")
    verify_patient_access(report["patient_user_id"], current_user)
    return report

@router.get("/{report_id}/download")
def download_report(report_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    report = report_service.get_report_details(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Medical report not found")
    verify_patient_access(report["patient_user_id"], current_user)
    
    file_path = Path(report["file_storage_path"])
    if not file_path.exists():
        # Fallback: create a readable representation so download never breaks
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"--- AI HEALTH CLINIC ---\nREPORT: {report['report_title']}\nCATEGORY: {report['report_category']}\nDATE: {report['test_date']}\n\n{report.get('extracted_raw_text', '')}")

    return FileResponse(
        path=str(file_path),
        filename=report["file_name"],
        media_type=report["file_mime_type"]
    )
