import os
import ctypes
import math
from pathlib import Path

C_MODULE_DIR = Path(__file__).resolve().parent

# Locate compiled dynamic library if available
_lib = None
possible_lib_names = ["medical_metrics.dll", "libmedical_metrics.so", "medical_metrics.so"]
for name in possible_lib_names:
    lib_path = C_MODULE_DIR / name
    if lib_path.exists():
        try:
            _lib = ctypes.CDLL(str(lib_path))
            break
        except Exception:
            _lib = None

def compute_bmi(weight_kg: float, height_m: float) -> float:
    """Computes Body Mass Index."""
    if _lib and hasattr(_lib, "calculate_bmi"):
        bmi_out = ctypes.c_double()
        res = _lib.calculate_bmi(ctypes.c_double(weight_kg), ctypes.c_double(height_m), ctypes.byref(bmi_out))
        if res == 0:
            return round(bmi_out.value, 2)
    # Pure Python fallback
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("Weight and height must be positive numbers.")
    return round(weight_kg / (height_m ** 2), 2)

def compute_bsa(weight_kg: float, height_cm: float) -> float:
    """Computes Body Surface Area (Mosteller)."""
    if _lib and hasattr(_lib, "calculate_bsa_mosteller"):
        bsa_out = ctypes.c_double()
        res = _lib.calculate_bsa_mosteller(ctypes.c_double(weight_kg), ctypes.c_double(height_cm), ctypes.byref(bsa_out))
        if res == 0:
            return round(bsa_out.value, 2)
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive numbers.")
    return round(math.sqrt((height_cm * weight_kg) / 3600.0), 2)

def compute_egfr(serum_creatinine_mg_dl: float, age_years: int, is_female: bool) -> float:
    """Computes Estimated Glomerular Filtration Rate (CKD-EPI 2021)."""
    if _lib and hasattr(_lib, "calculate_egfr_ckdepi"):
        egfr_out = ctypes.c_double()
        res = _lib.calculate_egfr_ckdepi(
            ctypes.c_double(serum_creatinine_mg_dl),
            ctypes.c_int(age_years),
            ctypes.c_int(1 if is_female else 0),
            ctypes.byref(egfr_out)
        )
        if res == 0:
            return round(egfr_out.value, 1)
    # Python fallback
    kappa = 0.7 if is_female else 0.9
    alpha = -0.241 if is_female else -0.302
    scr_ratio = serum_creatinine_mg_dl / kappa
    min_term = min(scr_ratio, 1.0)
    max_term = max(scr_ratio, 1.0)
    egfr = 142.0 * (min_term ** alpha) * (max_term ** -1.200) * (0.9938 ** age_years)
    if is_female:
        egfr *= 1.012
    return round(egfr, 1)
