import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_auth_token():
    resp = client.post("/api/auth/login", json={"email": "patient@clinic.com", "password": "Password@123"})
    return resp.json()["access_token"]

def test_timeline_retrieval_and_filtering():
    token = get_auth_token()
    
    # 1. Fetch all timeline events
    resp = client.get("/api/timeline", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 5
    
    # Verify chronological ordering (descending)
    dates = [e["event_date"] for e in events]
    assert dates == sorted(dates, reverse=True)

    # 2. Filter by category
    resp_filter = client.get("/api/timeline?event_type=Report Upload", headers={"Authorization": f"Bearer {token}"})
    assert resp_filter.status_code == 200
    report_events = resp_filter.json()
    assert all(e["event_type"] == "Report Upload" for e in report_events)

def test_timeline_event_detail_with_source_record():
    token = get_auth_token()
    resp = client.get("/api/timeline/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_id"] == 1
    assert "source_detail" in data
