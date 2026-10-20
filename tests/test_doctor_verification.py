import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_admin_token():
    resp = client.post("/api/auth/login", json={"email": "admin@clinic.com", "password": "Password@123"})
    return resp.json()["access_token"]

def test_admin_doctor_verification_queue():
    admin_token = get_admin_token()
    resp = client.get(
        "/api/admin/doctors/verification-queue?status=all",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    queue = resp.json()
    assert len(queue) >= 5 # 5 applicants seeded
    assert any("Dr." in doc["applicant_name"] for doc in queue)

def test_admin_review_approval():
    admin_token = get_admin_token()
    # Review first application
    resp = client.post(
        "/api/admin/doctors/review",
        json={"application_id": 1, "action": "Approved", "notes": "Medical council registration and degree certificates verified."},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert "Approved" in resp.json()["message"]
