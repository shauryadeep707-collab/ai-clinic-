from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from backend.app.schemas.medicine_schemas import PharmacyProviderResponse, PharmacySearchResponse
from backend.app.services.medicine_service import medicine_service

router = APIRouter(prefix="/api/pharmacies", tags=["Pharmacy Connect"])

@router.get("", response_model=List[PharmacyProviderResponse])
def get_pharmacy_providers():
    return medicine_service.get_pharmacy_providers()

@router.get("/search")
def search_pharmacies(query: str = Query(..., min_length=2)):
    # 1. Look up medicine info if present in local catalogue
    matched_meds = medicine_service.get_medicines_catalog(query)
    med_info = matched_meds[0] if matched_meds else None

    # 2. Generate verified pharmacy links
    destinations = medicine_service.generate_pharmacy_search_links(query)

    disclaimer = (
        "AI Health Clinic does not sell, dispense, or fulfill pharmaceutical orders directly. "
        "The links below redirect to verified official pharmacy platforms. Prescription requirements, "
        "pricing, availability, and delivery are governed solely by each respective pharmacy provider."
    )

    return {
        "query": query,
        "medicine_info": med_info,
        "destinations": destinations,
        "disclaimer": disclaimer
    }
