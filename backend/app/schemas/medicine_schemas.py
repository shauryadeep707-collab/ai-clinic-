from pydantic import BaseModel
from typing import Optional, List

class MedicineResponse(BaseModel):
    medicine_id: int
    generic_name: str
    brand_names: Optional[str] = None
    drug_class: Optional[str] = None
    common_uses: Optional[str] = None
    dosage_forms: Optional[str] = None
    precautions: Optional[str] = None
    contraindications: Optional[str] = None
    potential_side_effects: Optional[str] = None
    interaction_warnings: Optional[str] = None
    is_prescription_required: int
    source_reference: Optional[str] = None

class ReminderCreate(BaseModel):
    medicine_name: str
    dosage: str
    reminder_time: str # "09:00"
    days_of_week: Optional[str] = "Daily"
    start_date: Optional[str] = None

class ReminderResponse(BaseModel):
    reminder_id: int
    patient_user_id: int
    medicine_name: str
    dosage: str
    reminder_time: str
    days_of_week: str
    start_date: str
    end_date: Optional[str] = None
    is_active: int

class PharmacyProviderResponse(BaseModel):
    provider_id: int
    provider_name: str
    base_url: str
    search_url_template: Optional[str] = None
    category_tag: str
    is_active: int
    integration_status: str
    disclaimer_text: Optional[str] = None

class PharmacySearchResponse(BaseModel):
    query: str
    medicine_info: Optional[MedicineResponse] = None
    destinations: List[dict]
    disclaimer: str
