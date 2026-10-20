import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Health Clinic")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "healthclinic-super-secure-jwt-key-change-in-production-2026-xyz")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Database
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite").lower() # 'oracle' or 'sqlite'
    DB_FILE: str = os.getenv("DB_FILE", str(BASE_DIR / "ai_health_clinic.db"))
    
    # Oracle Database Settings
    ORACLE_USER: str = os.getenv("ORACLE_USER", "admin")
    ORACLE_PASSWORD: str = os.getenv("ORACLE_PASSWORD", "YourSecureOraclePassword123")
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1")
    ORACLE_CONFIG_DIR: str = os.getenv("ORACLE_CONFIG_DIR", "")
    ORACLE_WALLET_LOCATION: str = os.getenv("ORACLE_WALLET_LOCATION", "")
    
    # AI Engine
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "local_rule_engine") # 'gemini', 'ollama', or 'local_rule_engine'
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "medllama2")
    
    # File Storage
    UPLOAD_DIR: Path = BASE_DIR / "backend" / "uploads"
    REPORTS_DIR: Path = BASE_DIR / "backend" / "uploads" / "reports"
    DOCTOR_DOCS_DIR: Path = BASE_DIR / "backend" / "uploads" / "doctor_docs"
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15"))
    
    # External APIs
    DIGILOCKER_API_ENABLED: bool = os.getenv("DIGILOCKER_API_ENABLED", "false").lower() == "true"
    DIGILOCKER_CLIENT_ID: str = os.getenv("DIGILOCKER_CLIENT_ID", "")
    DIGILOCKER_CLIENT_SECRET: str = os.getenv("DIGILOCKER_CLIENT_SECRET", "")
    NMC_VERIFICATION_ENABLED: bool = os.getenv("NMC_VERIFICATION_ENABLED", "false").lower() == "true"
    PHARMACY_LIVE_INTEGRATION_ENABLED: bool = os.getenv("PHARMACY_LIVE_INTEGRATION_ENABLED", "false").lower() == "true"

settings = Settings()

# Ensure upload directories exist
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
settings.DOCTOR_DOCS_DIR.mkdir(parents=True, exist_ok=True)
