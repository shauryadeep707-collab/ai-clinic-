# AI Medicine Guidance & Pharmacy Connect

## Purpose
The `pharmacy_connect/` module connects patients to official, verified pharmacy channels without allowing AI to independently prescribe or sell medication.

## Verified Official Destinations
The platform routes search queries and category views to the following 7 verified official destinations:
1. **Amazon Pharmacy**: `https://www.amazon.in/pharmacy`
2. **Blinkit — Medicines**: `https://blinkit.com/cn/medicines/cid/287/7275`
3. **Swiggy Instamart**: `https://www.swiggy.com/instamart`
4. **Tata 1mg**: `https://www.1mg.com/`
5. **Apollo Pharmacy**: `https://www.apollopharmacy.in/`
6. **PharmEasy**: `https://pharmeasy.in/online-medicine-order`
7. **Netmeds**: `https://www.netmeds.com/c/`

## Clinical Safety Rules
- **No Direct Dispensing**: AI Health Clinic does not collect payment or fulfill medication orders.
- **Prescription Enforcement**: Prescription-only (Schedule H & H1) drugs and antibiotics mandate clinical consultation and genuine prescription verification on the external pharmacy platform.
- **Patient Allergy Cross-Referencing**: When a patient searches for a medicine, the system automatically checks their documented medical profile (e.g. penicillin allergy alert when searching Amoxicillin).
- **Commercial Transparency**: Pharmacy listings are neutral and unranked by commercial commission.
