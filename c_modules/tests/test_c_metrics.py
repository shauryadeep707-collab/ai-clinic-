import pytest
from c_modules.wrapper import compute_bmi, compute_bsa, compute_egfr

def test_compute_bmi():
    # 70 kg, 1.75 m -> 70 / (1.75^2) = 22.86
    bmi = compute_bmi(70.0, 1.75)
    assert abs(bmi - 22.86) < 0.1

def test_compute_bsa():
    # 70 kg, 175 cm -> sqrt((175 * 70) / 3600) = sqrt(3.40277) = 1.84 m^2
    bsa = compute_bsa(70.0, 175.0)
    assert abs(bsa - 1.84) < 0.1

def test_compute_egfr():
    # Serum creatinine 0.9, Age 30, Male (0)
    egfr = compute_egfr(0.9, 30, False)
    assert egfr > 90.0 # Normal renal function
