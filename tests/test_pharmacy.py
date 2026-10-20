import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_auth_token():
    resp = client.post("/api/auth/login", json={"email": "patient@clinic.com", "password": "Password@123"})
    return resp.json()["access_token"]

def test_pharmacy_providers_list():
    resp = client.get("/api/pharmacies")
    assert resp.status_code == 200
    providers = resp.json()
    assert len(providers) == 7
    names = [p["provider_name"] for p in providers]
    assert "Amazon Pharmacy" in names
    assert "Blinkit — Medicines" in names
    assert "Tata 1mg" in names
    assert "Apollo Pharmacy" in names
    assert "PharmEasy" in names
    assert "Netmeds" in names

def test_pharmacy_search_links_and_disclaimer():
    resp = client.get("/api/pharmacies/search?query=Paracetamol")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["destinations"]) == 7
    assert "disclaimer" in data
    assert "does not sell" in data["disclaimer"].lower()

def test_patient_allergy_warning():
    token = get_auth_token()
    # Rohan Sharma has documented Penicillin allergy
    resp = client.post(
        "/api/medicines/allergy-check?medicine_name=Amoxicillin",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_allergy_warning"] is True
    assert any("ALLERGY ALERT" in alert for alert in data["alerts"])
