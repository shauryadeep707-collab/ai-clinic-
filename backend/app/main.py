import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from backend.app.config.settings import settings
from backend.app.database.connection import init_database
from backend.app.routers import (
    auth,
    patients,
    consultations,
    medical_reports,
    timeline,
    doctors,
    appointments,
    medicines,
    pharmacies,
    admin
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_health_clinic")

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-Stack Healthcare Platform with AI, Medical History, Unified Timeline, Doctor Verification, and Pharmacy Integration.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(consultations.router)
app.include_router(medical_reports.router)
app.include_router(timeline.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(medicines.router)
app.include_router(pharmacies.router)
app.include_router(admin.router)

# Mount Static Directories
FRONTEND_DIR = settings.UPLOAD_DIR.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend_static")

if settings.REPORTS_DIR.exists():
    app.mount("/storage/reports", StaticFiles(directory=str(settings.REPORTS_DIR)), name="reports_storage")

@app.on_event("startup")
def startup_event():
    logger.info(f"Starting {settings.APP_NAME}...")
    init_database()
    logger.info("Application startup and database verification completed.")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "database_engine": settings.DB_ENGINE,
        "ai_provider": settings.AI_PROVIDER
    }

@app.get("/")
def read_root():
    index_path = FRONTEND_DIR / "html" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": f"Welcome to {settings.APP_NAME} API. Access /docs for API documentation."}
