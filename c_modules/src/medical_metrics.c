#include <stdio.h>
#include <math.h>
#include "../include/medical_metrics.h"

int calculate_bmi(double weight_kg, double height_m, double *bmi_out) {
    if (weight_kg <= 0.0 || height_m <= 0.0 || bmi_out == NULL) {
        return -1; // Invalid input
    }
    *bmi_out = weight_kg / (height_m * height_m);
    return 0; // Success
}

int calculate_bsa_mosteller(double weight_kg, double height_cm, double *bsa_out) {
    if (weight_kg <= 0.0 || height_cm <= 0.0 || bsa_out == NULL) {
        return -1;
    }
    *bsa_out = sqrt((height_cm * weight_kg) / 3600.0);
    return 0;
}

int calculate_egfr_ckdepi(double serum_creatinine_mg_dl, int age_years, int is_female, double *egfr_out) {
    if (serum_creatinine_mg_dl <= 0.0 || age_years <= 0 || egfr_out == NULL) {
        return -1;
    }
    double kappa = is_female ? 0.7 : 0.9;
    double alpha = is_female ? -0.241 : -0.302;
    double scr_ratio = serum_creatinine_mg_dl / kappa;
    double min_term = (scr_ratio < 1.0) ? scr_ratio : 1.0;
    double max_term = (scr_ratio > 1.0) ? scr_ratio : 1.0;

    double egfr = 142.0 * pow(min_term, alpha) * pow(max_term, -1.200) * pow(0.9938, (double)age_years);
    if (is_female) {
        egfr *= 1.012;
    }
    *egfr_out = egfr;
    return 0;
}

int calculate_clarks_pediatric_dose(double adult_dose_mg, double child_weight_kg, double *child_dose_out) {
    if (adult_dose_mg <= 0.0 || child_weight_kg <= 0.0 || child_dose_out == NULL) {
        return -1;
    }
    *child_dose_out = (child_weight_kg / 68.0) * adult_dose_mg;
    return 0;
}
