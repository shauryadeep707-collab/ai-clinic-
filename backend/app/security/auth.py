from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.app.config.settings import settings
from backend.app.database.connection import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or session expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    db = get_db()
    user = db.query_one("SELECT user_id, email, role, full_name, phone, is_active, is_verified FROM users WHERE user_id = ?", (user_id,))
    if not user:
        raise credentials_exception
    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")
    return user

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

def verify_patient_access(target_patient_user_id: int, current_user: Dict[str, Any]):
    """
    Enforces HIPAA / Data Protection data isolation:
    - Patients can ONLY access their own records.
    - Admins can access for audit/support purposes.
    - Doctors can only access if authorized via explicit sharing permission or active appointment.
    """
    if current_user["role"] == "admin":
        return True
    if current_user["role"] == "patient":
        if current_user["user_id"] != target_patient_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security violation: Unauthorized attempt to access another patient's medical records."
            )
        return True
    if current_user["role"] == "doctor":
        db = get_db()
        # Check active record sharing permission
        permission = db.query_one(
            "SELECT permission_id FROM record_sharing_permissions WHERE patient_user_id = ? AND doctor_user_id = ?",
            (target_patient_user_id, current_user["user_id"])
        )
        if permission:
            return True
        # Check if doctor has an appointment with the patient
        appt = db.query_one(
            "SELECT a.appointment_id FROM appointments a JOIN doctor_profiles d ON a.doctor_id = d.doctor_id WHERE a.patient_user_id = ? AND d.user_id = ?",
            (target_patient_user_id, current_user["user_id"])
        )
        if appt:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Patient has not authorized this doctor to view their records."
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
