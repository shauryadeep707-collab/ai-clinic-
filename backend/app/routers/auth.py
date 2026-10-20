from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from backend.app.schemas.auth_schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse, PasswordResetRequest
from backend.app.database.connection import get_db
from backend.app.security.auth import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    db = get_db()
    existing = db.query_one("SELECT user_id FROM users WHERE LOWER(email) = LOWER(?)", (req.email,))
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    pwd_hash = hash_password(req.password)
    user_id = db.execute_write(
        "INSERT INTO users (email, password_hash, role, full_name, phone, is_active, is_verified) VALUES (?, ?, ?, ?, ?, 1, 0)",
        (req.email.lower(), pwd_hash, req.role, req.full_name, req.phone or "")
    )

    if req.role == "patient":
        db.execute_write(
            "INSERT INTO patient_profiles (user_id) VALUES (?)",
            (user_id,)
        )
    elif req.role == "doctor":
        doc_id = db.execute_write("""
            INSERT INTO doctor_profiles 
            (user_id, specialization, qualification_summary, medical_reg_number, registration_council, verification_status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (
            user_id,
            req.specialization or "General Medicine",
            req.qualification_summary or "Medical Degree",
            req.medical_reg_number or f"REG-{user_id}-2026",
            req.registration_council or "State Medical Council"
        ))
        # Create pending application in queue
        db.execute_write(
            "INSERT INTO doctor_applications (doctor_id, status) VALUES (?, 'Pending')",
            (doc_id,)
        )

    token = create_access_token({"sub": str(user_id), "role": req.role, "email": req.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "role": req.role,
        "full_name": req.full_name,
        "email": req.email
    }

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    db = get_db()
    user = db.query_one("SELECT user_id, email, password_hash, role, full_name, is_active FROM users WHERE LOWER(email) = LOWER(?)", (req.email,))
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated. Please contact support.")

    token = create_access_token({"sub": str(user["user_id"]), "role": user["role"], "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["user_id"],
        "role": user["role"],
        "full_name": user["full_name"],
        "email": user["email"]
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    return user

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully."}

@router.post("/reset-password")
def reset_password(req: PasswordResetRequest):
    db = get_db()
    user = db.query_one("SELECT user_id FROM users WHERE LOWER(email) = LOWER(?)", (req.email,))
    if not user:
        raise HTTPException(status_code=404, detail="No user found with the specified email.")
    new_hash = hash_password(req.new_password)
    db.execute_write("UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", (new_hash, user["user_id"]))
    return {"message": "Password reset successfully. You can now log in with your new password."}
