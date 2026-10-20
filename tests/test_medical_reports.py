import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from ai.report_summarization.summarizer import extract_and_summarize_report

client = TestClient(app)

def get_auth_token():
    resp = client.post("/api/auth/login", json={"email": "patient@clinic.com", "password": "Password@123"})
    return resp.json()["access_token"]

def test_extract_and_summarize_normal_and_abnormal():
    raw_text = "Patient Lab Results: Hemoglobin: 14.2 g/dL. Total WBC: 7200 /uL. Vitamin D: 18.2 ng/mL. Fasting Blood Sugar: 94 mg/dL."
    result = extract_and_summarize_report(raw_text, "Blood Panel")
    
    assert len(result["extracted_measurements"]) >= 3
    # Vitamin D (18.2) is below normal range (30-100)
    assert any(m["test_metric_name"] == "Vitamin D (25-OH)" and m["status_flag"] == "Low" for m in result["extracted_measurements"])
    # Hemoglobin is Normal
    assert any(m["test_metric_name"] == "Hemoglobin" and m["status_flag"] == "Normal" for m in result["extracted_measurements"])
    assert "questions_for_doctor" in result

def test_list_reports_api():
    token = get_auth_token()
    resp = client.get("/api/medical-reports", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    reports = resp.json()
    assert len(reports) >= 1
    assert any("Blood Test" in r["report_title"] for r in reports)

def test_report_detail_api():
    token = get_auth_token()
    resp = client.get("/api/medical-reports/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_id"] == 1
    assert "ai_summary" in data
    assert "measurements" in data
