import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_login_success():
    resp = client.post("/api/auth/login", json={
        "email": "patient@clinic.com",
        "password": "Password@123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "patient"
    assert data["full_name"] == "Rohan Sharma"

def test_login_invalid_password():
    resp = client.post("/api/auth/login", json={
        "email": "patient@clinic.com",
        "password": "WrongPassword!"
    })
    assert resp.status_code == 401

import time

def test_registration_and_duplicate_prevention():
    new_email = f"test.patient.{int(time.time()*1000)}@clinic.com"
    resp = client.post("/api/auth/register", json={
        "email": new_email,
        "password": "Password@123",
        "full_name": "Test New User",
        "role": "patient"
    })
    assert resp.status_code == 200
    assert resp.json()["email"] == new_email

    # Duplicate registration must fail
    dup_resp = client.post("/api/auth/register", json={
        "email": new_email,
        "password": "Password@123",
        "full_name": "Duplicate User",
        "role": "patient"
    })
    assert dup_resp.status_code == 400
