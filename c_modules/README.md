# C Modules — High-Performance Medical Metrics

## Purpose
This directory provides an optional C module for high-throughput, low-latency clinical biometric calculations:
1. **BMI (Body Mass Index)**: Metric physiological index calculation.
2. **BSA (Body Surface Area)**: Mosteller clinical standard used in oncology and critical care dosage calculation.
3. **eGFR (Estimated Glomerular Filtration Rate)**: CKD-EPI 2021 race-free equation for renal function evaluation.
4. **Clark's Pediatric Dosage**: Pediatric medicine dose scaling based on pediatric weight against standard adult benchmark (68 kg).

## Files
- `include/medical_metrics.h`: C header file with extern "C" bindings.
- `src/medical_metrics.c`: Pure C source implementation.
- `wrapper.py`: Python ctypes interface with pure Python fallback.
- `tests/test_c_metrics.py`: Verification test suite.

## Compilation Instructions
### Linux / macOS:
```bash
gcc -O3 -shared -fPIC src/medical_metrics.c -o libmedical_metrics.so -lm
```

### Windows (MSVC):
```cmd
cl /O2 /LD src/medical_metrics.c /Fe:medical_metrics.dll
```

### Windows (MinGW GCC):
```cmd
gcc -O3 -shared src/medical_metrics.c -o medical_metrics.dll -lm
```
