import re
from typing import Dict, Any, List

# Standard Reference Ranges for Key Common Lab Parameters
REFERENCE_RANGES = {
    "hemoglobin": {"name": "Hemoglobin", "unit": "g/dL", "low": 13.0, "high": 17.0, "pattern": r"hemoglobin\s*[:=\-]?\s*([0-9]+(?:\.[0-9]+)?)"},
    "wbc": {"name": "Total Leukocytes (WBC)", "unit": "/uL", "low": 4000.0, "high": 11000.0, "pattern": r"(?:total\s+wbc|wbc|leukocytes)\s*[:=\-]?\s*([0-9,]+)"},
    "platelets": {"name": "Platelet Count", "unit": "/uL", "low": 150000.0, "high": 450000.0, "pattern": r"platelets?\s*[:=\-]?\s*([0-9,]+)"},
    "blood_sugar": {"name": "Fasting Blood Sugar", "unit": "mg/dL", "low": 70.0, "high": 99.0, "pattern": r"(?:fasting\s+blood\s+sugar|fbs|glucose)\s*[:=\-]?\s*([0-9]+(?:\.[0-9]+)?)"},
    "vitamin_d": {"name": "Vitamin D (25-OH)", "unit": "ng/mL", "low": 30.0, "high": 100.0, "pattern": r"vitamin\s+d\s*(?:\(25-oh\))?\s*[:=\-]?\s*([0-9]+(?:\.[0-9]+)?)"},
    "creatinine": {"name": "Serum Creatinine", "unit": "mg/dL", "low": 0.6, "high": 1.2, "pattern": r"creatinine\s*[:=\-]?\s*([0-9]+(?:\.[0-9]+)?)"},
}

def extract_and_summarize_report(raw_text: str, report_title: str) -> Dict[str, Any]:
    """
    Parses document text, extracts numerical lab parameters, checks against clinical reference ranges,
    and produces grounded summary and questions for doctor without fabricating data.
    """
    extracted_measurements: List[Dict[str, Any]] = []
    normal_list: List[str] = []
    abnormal_list: List[str] = []

    text_lower = raw_text.lower()

    for key, spec in REFERENCE_RANGES.items():
        match = re.search(spec["pattern"], text_lower, re.IGNORECASE)
        if match:
            raw_val_str = match.group(1).replace(",", "")
            try:
                val = float(raw_val_str)
                status = "Normal"
                if val < spec["low"]:
                    status = "Low"
                    abnormal_list.append(f"{spec['name']} is {val} {spec['unit']} (Below normal: {spec['low']} - {spec['high']} {spec['unit']})")
                elif val > spec["high"]:
                    status = "High"
                    abnormal_list.append(f"{spec['name']} is {val} {spec['unit']} (Above normal: {spec['low']} - {spec['high']} {spec['unit']})")
                else:
                    normal_list.append(f"{spec['name']} ({val} {spec['unit']})")

                extracted_measurements.append({
                    "test_metric_name": spec["name"],
                    "observed_value": val,
                    "unit": spec["unit"],
                    "reference_range_low": spec["low"],
                    "reference_range_high": spec["high"],
                    "status_flag": status,
                    "notes": f"Standard clinical reference range {spec['low']} - {spec['high']} {spec['unit']}"
                })
            except ValueError:
                pass

    # Build grounded textual summary
    if extracted_measurements:
        if abnormal_list:
            ai_summary = (
                f"Your {report_title} shows mostly normal baseline values. "
                f"However, the following metric(s) require clinical attention: {'; '.join(abnormal_list)}. "
                f"Normal parameters: {', '.join(normal_list) if normal_list else 'None detected in this range'}."
            )
            key_findings = f"Attention required for {len(abnormal_list)} parameter(s): {', '.join(abnormal_list)}."
            questions = (
                "1. Does the abnormal result require supplementation or medication?\n"
                "2. When should this test be repeated to track progression?\n"
                "3. Are dietary or lifestyle modifications recommended?"
            )
        else:
            ai_summary = f"All tested metrics in your {report_title} fall within standard clinical reference ranges."
            key_findings = "No significant abnormalities detected in the extracted parameters."
            questions = "1. How frequently should routine wellness monitoring tests be conducted?"
    else:
        # Non-numerical report or radiology/imaging report
        ai_summary = f"Review of {report_title}: Report text was processed successfully. Medical findings should be reviewed with your consulting physician."
        key_findings = raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
        questions = "1. What are the key takeaways from these clinical findings?"

    return {
        "extracted_measurements": extracted_measurements,
        "ai_summary_text": ai_summary,
        "key_findings": key_findings,
        "normal_metrics": ", ".join(normal_list) if normal_list else "None noted",
        "abnormal_metrics": ", ".join(abnormal_list) if abnormal_list else "None detected",
        "questions_for_doctor": questions,
        "source_grounding_disclaimer": "AI-generated summary based strictly on document text. Not a clinical diagnosis."
    }
