import urllib.parse
from typing import List, Dict, Any, Optional
from backend.app.database.connection import get_db

class MedicineService:
    @staticmethod
    def get_medicines_catalog(query: Optional[str] = None) -> List[Dict[str, Any]]:
        db = get_db()
        sql = "SELECT * FROM medicines"
        params = []
        if query:
            sql += " WHERE LOWER(generic_name) LIKE ? OR LOWER(brand_names) LIKE ? OR LOWER(drug_class) LIKE ?"
            q = f"%{query.lower()}%"
            params.extend([q, q, q])
        sql += " ORDER BY generic_name ASC"
        return db.query_all(sql, tuple(params))

    @staticmethod
    def get_medicine_by_id(medicine_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        return db.query_one("SELECT * FROM medicines WHERE medicine_id = ?", (medicine_id,))

    @staticmethod
    def check_patient_allergies_and_interactions(patient_user_id: int, medicine_name: str) -> Dict[str, Any]:
        """
        Safety Check: cross-references candidate medicine against patient's known allergies.
        """
        db = get_db()
        patient = db.query_one("SELECT known_allergies, current_medications FROM patient_profiles WHERE user_id = ?", (patient_user_id,))
        alerts = []
        
        if patient and patient.get("known_allergies"):
            allergies = patient["known_allergies"].lower()
            med_lower = medicine_name.lower()
            
            # Clinical cross-reactivity mapping
            if "penicillin" in allergies and any(p in med_lower for p in ["amoxicillin", "ampicillin", "augmentin", "penicillin"]):
                alerts.append(f"⚠️ ALLERGY ALERT: Patient has a documented allergy to '{patient['known_allergies']}'. '{medicine_name}' belongs to the penicillin antibiotic class and may trigger severe anaphylactic reactions.")
            elif "sulfa" in allergies and "sulfa" in med_lower:
                alerts.append(f"⚠️ ALLERGY ALERT: Cross-reactivity warning with patient's documented allergy: '{patient['known_allergies']}'.")
            elif any(token in med_lower for token in allergies.split(",")):
                alerts.append(f"⚠️ POTENTIAL ALLERGY WARNING: Match found with documented allergies: '{patient['known_allergies']}'.")

        return {
            "has_allergy_warning": len(alerts) > 0,
            "alerts": alerts,
            "known_allergies": patient.get("known_allergies") if patient else "None documented",
            "current_medications": patient.get("current_medications") if patient else "None documented"
        }

    @staticmethod
    def get_pharmacy_providers() -> List[Dict[str, Any]]:
        db = get_db()
        return db.query_all("SELECT * FROM pharmacy_providers WHERE is_active = 1 ORDER BY provider_id ASC")

    @staticmethod
    def generate_pharmacy_search_links(medicine_query: str) -> List[Dict[str, Any]]:
        """
        Generates official external landing and search links for verified Indian pharmacies.
        """
        providers = MedicineService.get_pharmacy_providers()
        encoded_query = urllib.parse.quote_plus(medicine_query.strip())
        results = []

        for p in providers:
            tmpl = p.get("search_url_template")
            if tmpl:
                url = tmpl.replace("{query}", encoded_query)
            else:
                url = p["base_url"]

            results.append({
                "provider_id": p["provider_id"],
                "provider_name": p["provider_name"],
                "category_tag": p["category_tag"],
                "search_url": url,
                "base_url": p["base_url"],
                "integration_status": p["integration_status"],
                "disclaimer_text": p["disclaimer_text"]
            })
        return results

    @staticmethod
    def get_patient_reminders(patient_user_id: int) -> List[Dict[str, Any]]:
        db = get_db()
        return db.query_all("""
            SELECT * FROM medicine_reminders 
            WHERE patient_user_id = ? 
            ORDER BY reminder_time ASC
        """, (patient_user_id,))

    @staticmethod
    def create_reminder(
        patient_user_id: int,
        medicine_name: str,
        dosage: str,
        reminder_time: str,
        days_of_week: str = "Daily",
        start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        db = get_db()
        effective_start = start_date if start_date else "2024-10-18"
        reminder_id = db.execute_write("""
            INSERT INTO medicine_reminders 
            (patient_user_id, medicine_name, dosage, reminder_time, days_of_week, start_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (patient_user_id, medicine_name, dosage, reminder_time, days_of_week, effective_start))
        return db.query_one("SELECT * FROM medicine_reminders WHERE reminder_id = ?", (reminder_id,))

    @staticmethod
    def toggle_reminder(reminder_id: int, patient_user_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        rem = db.query_one("SELECT * FROM medicine_reminders WHERE reminder_id = ? AND patient_user_id = ?", (reminder_id, patient_user_id))
        if not rem:
            return None
        new_active = 0 if rem["is_active"] == 1 else 1
        db.execute_write("UPDATE medicine_reminders SET is_active = ? WHERE reminder_id = ?", (new_active, reminder_id))
        return db.query_one("SELECT * FROM medicine_reminders WHERE reminder_id = ?", (reminder_id,))

medicine_service = MedicineService()
