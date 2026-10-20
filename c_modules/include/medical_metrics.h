#ifndef MEDICAL_METRICS_H
#define MEDICAL_METRICS_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Calculates Body Mass Index (BMI).
 * Formula: weight (kg) / (height (m) * height (m))
 */
int calculate_bmi(double weight_kg, double height_m, double *bmi_out);

/**
 * Calculates Body Surface Area (BSA) using Mosteller formula.
 * Formula: sqrt((height_cm * weight_kg) / 3600)
 */
int calculate_bsa_mosteller(double weight_kg, double height_cm, double *bsa_out);

/**
 * Calculates Estimated Glomerular Filtration Rate (eGFR) using CKD-EPI 2021 formula.
 */
int calculate_egfr_ckdepi(double serum_creatinine_mg_dl, int age_years, int is_female, double *egfr_out);

/**
 * Calculates Pediatric Dosage using Clark's Rule.
 * Formula: (Child's Weight in kg / 68 kg) * Adult Dose
 */
int calculate_clarks_pediatric_dose(double adult_dose_mg, double child_weight_kg, double *child_dose_out);

#ifdef __cplusplus
}
#endif

#endif /* MEDICAL_METRICS_H */
