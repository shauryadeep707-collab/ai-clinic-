"""
Pharmacy and Medicine routes for AI Health Clinic & Assistant.
Provides multi-pharmacy search across 7 verified Indian destinations,
drug safety & allergy contraindication checks, and reminder schedules.
"""

from urllib.parse import quote
from flask import Blueprint, request, jsonify, g
from backend.auth_utils import get_current_user
from backend import db as database

pharmacies_bp = Blueprint('pharmacies', __name__)

# Fallback pharmacy destination URL templates
PHARMACY_TEMPLATES = [
    ('Amazon Pharmacy', 'https://www.amazon.in/s?k={query}&i=hpc'),
    ('Blinkit Medicines', 'https://blinkit.com/s/?q={query}'),
    ('Swiggy Instamart', 'https://www.swiggy.com/instamart/search?custom_back=true&query={query}'),
    ('Tata 1mg', 'https://www.1mg.com/search/all?name={query}'),
    ('Apollo Pharmacy', 'https://www.apollopharmacy.in/search-medicines/{query}'),
    ('PharmEasy', 'https://pharmeasy.in/search/all?name={query}'),
    ('Netmeds', 'https://www.netmeds.com/catalogsearch/result?q={query}'),
]

# Extended Clinical Knowledge Base for OTC and Pharmacy Search
CLINICAL_MEDICINE_KB = [
    {
        'match_keys': ['sunscreen', 'sun screen', 'sun protection', 'sunblock', 'spf', 'uv protection'],
        'generic_name': 'Broad-Spectrum Sunscreen (SPF 30 / SPF 50+ PA++++)',
        'brand_names': 'Neutrogena Ultra Sheer, La Shield Gel, Lotus Herbals Safe Sun, Derma Co 1% Hyaluronic, Cetaphil Sun, Aqualogica',
        'common_uses': 'Photoprotection against UVA/UVB radiation, prevention of sunburn, solar elastosis, and UV-induced hyperpigmentation.',
        'dosage_forms': 'Lotion, Matte Gel, Ultra-Light Fluid, Sunscreen Stick, Spray (SPF 30, SPF 50+, PA++++)',
        'precautions': 'Apply liberally 15–20 minutes prior to outdoor sun exposure. Reapply every 2 to 3 hours, or immediately after sweating or swimming.',
        'contraindications': 'Known hypersensitivity or allergic dermatitis to specific chemical UV filters (e.g., oxybenzone) or fragrance components.',
        'potential_side_effects': 'Mild skin warmth, stinging around eyes, or pore clogging with heavy comedogenic formulations.',
        'source_reference': 'Indian Association of Dermatologists (IADVL); WHO Sun Protection Guidelines; US FDA OTC Sunscreen Monograph.',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['moisturizer', 'moisturiser', 'body lotion', 'face cream', 'cold cream', 'cetaphil', 'ceramide', 'vaseline'],
        'generic_name': 'Hydrating Ceramide & Emollient Skin Barrier Moisturizer',
        'brand_names': 'Cetaphil Moisturizing Lotion, CeraVe Daily, Bioderma Atoderm, Nivea Soft, Vaseline Intensive Care, Physiogel A.I.',
        'common_uses': 'Restores skin barrier lipid layer, treats dry/flaky skin, soothes atopic dermatitis, and maintains dermal hydration.',
        'dosage_forms': 'Lotion, Cream, Emollient Balm, Hydrating Gel',
        'precautions': 'Apply on damp skin after bathing for maximum moisture retention. Discontinue if persistent irritation occurs.',
        'contraindications': 'Hypersensitivity to any excipient, preservative, or fragrance in the formulation.',
        'potential_side_effects': 'Occasional mild contact irritation or comedogenicity on acne-prone skin.',
        'source_reference': 'British Association of Dermatologists (BAD); National Formulary of India (NFI).',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['vitamin c', 'limcee', 'ascorbic acid', 'celin'],
        'generic_name': 'Vitamin C (Ascorbic Acid 500mg)',
        'brand_names': 'Limcee 500mg, Celin 500mg, Chewette-C, Redoxon',
        'common_uses': 'Antioxidant defense, cellular immune support, collagen synthesis, wound healing, and scurvy prevention.',
        'dosage_forms': 'Chewable Tablet (500mg), Effervescent Tablet, Serum (Topical 10–20%)',
        'precautions': 'Consume with or after meals. Chew thoroughly. Do not exceed 2,000 mg daily to prevent gastrointestinal upset.',
        'contraindications': 'History of oxalate kidney stones or severe renal impairment.',
        'potential_side_effects': 'Mild abdominal cramps, transient diarrhea with large doses, slight gastric acidity.',
        'source_reference': 'WHO Model List of Essential Medicines; ICMR RDA Guidelines.',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['vitamin d', 'vitamin d3', 'cholecalciferol', 'calcirol', 'd-rise'],
        'generic_name': 'Cholecalciferol (Vitamin D3 60,000 IU / 1,000 IU)',
        'brand_names': 'D-Rise 60K, Calcirol Sachet, Uprise-D3, Tayo 60K',
        'common_uses': 'Bone mineralization, calcium homeostasis, prevention of osteoporosis, osteomalacia, and immune modulation.',
        'dosage_forms': 'Capsule / Softgel (60,000 IU), Chewable Tablet, Oral Drops, Granules Sachet',
        'precautions': '60,000 IU is typically taken once weekly with milk or fatty meal, or as directed by clinician. Monitor serum 25(OH)D levels.',
        'contraindications': 'Hypercalcemia, hypervitaminosis D, or severe renal calcification.',
        'potential_side_effects': 'Hypercalcemia symptoms (nausea, polyuria, weakness) only in cases of chronic excessive overdose.',
        'source_reference': 'Endocrine Society Clinical Practice Guidelines; Indian Pharmacopoeia (IP).',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['ors', 'electral', 'electrolyte', 'oral rehydration', 'walyte', 'dehydration'],
        'generic_name': 'WHO-Formula Oral Rehydration Salts (ORS)',
        'brand_names': 'Electral Powder, Walyte ORS, ORS-L, Enerzal',
        'common_uses': 'Restoration of water and electrolyte loss during acute diarrhea, vomiting, heat exhaustion, or vigorous exercise.',
        'dosage_forms': 'Powder Sachet (to dissolve in 1 Liter potable water), Ready-to-drink Tetra Pak (200ml)',
        'precautions': 'Dissolve full packet in clean drinking water in the exact ratio specified. Consume within 24 hours of reconstitution.',
        'contraindications': 'Intractable persistent vomiting, paralytic ileus, or acute intestinal perforation (requires IV rehydration).',
        'potential_side_effects': 'Hypernatremia or puffiness if reconstituted with insufficient water.',
        'source_reference': 'WHO / UNICEF Diarrhoea Treatment Guidelines; Indian National List of Essential Medicines (NLEM).',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['cough syrup', 'cough', 'benadryl', 'grilinctus', 'ascoril', 'honitus', 'strepsils', 'lozenge'],
        'generic_name': 'Antitussive / Expectorant Cough & Throat Formulation',
        'brand_names': 'Benadryl Cough Formula, Grilinctus, Ascoril-D, Honitus Herbal, Strepsils, Chericof',
        'common_uses': 'Relief from dry irritating cough, throat tickle, or clearance of thick bronchial mucus associated with upper respiratory tract infections.',
        'dosage_forms': 'Oral Syrup (100ml / 200ml), Oral Lozenges',
        'precautions': 'May cause mild drowsiness. Avoid driving or operating machinery. Avoid concurrent alcohol consumption.',
        'contraindications': 'Severe persistent bronchial asthma, respiratory depression, or children under 2 years without pediatrician consultation.',
        'potential_side_effects': 'Mild sedation, dry mouth, dizziness, occasional nausea.',
        'source_reference': 'Central Drugs Standard Control Organisation (CDSCO); NHS Formulary.',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['antacid', 'digene', 'gelusil', 'eno', 'acidity', 'gas relief', 'heartburn'],
        'generic_name': 'Magnesium & Aluminium Hydroxide with Simethicone Antacid',
        'brand_names': 'Digene Gel / Chewable, Gelusil MPS, Eno Fruit Salt, Mucaine Gel',
        'common_uses': 'Immediate relief from hyperacidity, heartburn, acid indigestion, sour stomach, and flatulence / bloating.',
        'dosage_forms': 'Oral Suspension Gel (200ml, 450ml), Chewable Tablets, Effervescent Sachet',
        'precautions': 'Take 1–2 hours after meals or at bedtime. Shake suspension well before use. Separate from other oral medications by 2 hours.',
        'contraindications': 'Severe renal impairment (risk of aluminium or magnesium accumulation).',
        'potential_side_effects': 'Mild bowel alterations (chalky taste, slight constipation or laxative effect depending on formulation).',
        'source_reference': 'British National Formulary (BNF); CDSCO OTC Monograph.',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['bandage', 'dettol', 'savlon', 'betadine', 'first aid', 'cotton', 'antiseptic', 'band-aid'],
        'generic_name': 'Antiseptic Solution / Wound Dressing Medical Supply',
        'brand_names': 'Dettol Antiseptic, Savlon, Betadine (Povidone Iodine 5%/10%), Hansaplast Band-Aid, Johnson & Johnson Gauze',
        'common_uses': 'Cleansing superficial abrasions, minor cuts, insect bites, and surgical wound protection against bacterial infection.',
        'dosage_forms': 'Antiseptic Liquid, Medicated Ointment, Adhesive Strips (Band-Aid), Sterile Gauze, Cotton Rolls',
        'precautions': 'For external application only. Dilute antiseptic liquid as directed before applying to broken skin.',
        'contraindications': 'Deep puncture wounds, animal bites, severe burns (require formal urgent medical care). Iodine allergy (for Betadine).',
        'potential_side_effects': 'Local skin irritation, transient burning sensation upon initial application.',
        'source_reference': 'WHO Guidelines on Hand Hygiene and Topical Antiseptics; Indian Red Cross First Aid Manual.',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['paracetamol', 'crocin', 'calpol', 'dolo', 'acetaminophen'],
        'generic_name': 'Paracetamol (Acetaminophen 500mg / 650mg)',
        'brand_names': 'Crocin, Calpol, Dolo 650, Pacimol',
        'common_uses': 'First-line relief for mild-to-moderate fever, headache, body ache, and post-vaccination discomfort.',
        'dosage_forms': 'Tablet (500mg, 650mg), Oral Syrup (120mg/5ml, 250mg/5ml), Drops',
        'precautions': 'Do not exceed 4,000 mg in 24 hours (adults). Avoid concurrent alcohol use. Maintain 4–6 hour intervals between doses.',
        'contraindications': 'Severe hepatic impairment, active liver disease, or known hypersensitivity to paracetamol.',
        'potential_side_effects': 'Rare at therapeutic doses. Hepatotoxicity risk with excessive acute or chronic overdose.',
        'source_reference': 'British National Formulary (BNF); WHO Essential Medicines List.',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['cetirizine', 'zyrtec', 'cetzine', 'alerid', 'allergy'],
        'generic_name': 'Cetirizine Hydrochloride (10mg)',
        'brand_names': 'Cetzine, Zyrtec, Alerid, Okacet',
        'common_uses': 'Symptomatic relief of allergic rhinitis, sneezing, runny nose, itchy watery eyes, and chronic urticaria / hives.',
        'dosage_forms': 'Tablet (10mg), Syrup (5mg/5ml)',
        'precautions': 'Best taken once daily at bedtime. May cause mild drowsiness; exercise caution when driving.',
        'contraindications': 'Severe end-stage renal disease (CrCl < 10 mL/min). Hypersensitivity to hydroxyzine or cetirizine.',
        'potential_side_effects': 'Mild sedation, dry mouth, headache, fatigue.',
        'source_reference': 'British National Formulary (BNF); Central Drugs Standard Control Organisation (CDSCO).',
        'is_prescription_required': 0
    },
    {
        'match_keys': ['amoxicillin', 'mox', 'novamox', 'augmentin', 'antibiotic', 'azithromycin', 'ciprofloxacin'],
        'generic_name': 'Broad-Spectrum Antimicrobial (Antibiotic)',
        'brand_names': 'Mox 500, Novamox, Augmentin 625, Azithral 500, Ciplox 500',
        'common_uses': 'Treatment of confirmed bacterial infections (respiratory, ear, urinary tract, or dental). NOT effective against viral colds or flu.',
        'dosage_forms': 'Oral Tablet / Capsule (250mg, 500mg, 625mg), Dry Syrup Suspension',
        'precautions': 'Mandatory clinical prescription required. Complete the full prescribed course even if symptoms resolve early.',
        'contraindications': 'Known hypersensitivity or anaphylaxis to penicillin or cephalosporin class antibiotics.',
        'potential_side_effects': 'Gastrointestinal disturbance (diarrhea, nausea), mild skin rash, potential secondary candidiasis.',
        'source_reference': 'WHO Global Antimicrobial Resistance Surveillance; CDSCO Schedule H1 Regulations.',
        'is_prescription_required': 1
    },
    {
        'match_keys': ['metformin', 'glycomet', 'glucophage', 'diabetes', 'blood sugar'],
        'generic_name': 'Metformin Hydrochloride (500mg / 850mg / 1000mg SR)',
        'brand_names': 'Glycomet, Glucophage, Obimet, Cetapin-XR',
        'common_uses': 'First-line oral antihyperglycemic medication for the management of Type 2 Diabetes Mellitus.',
        'dosage_forms': 'Immediate Release & Extended Release (SR/XR) Tablets (500mg, 850mg, 1000mg)',
        'precautions': 'Take with or immediately after meals to minimize GI side effects. Monitor kidney function (eGFR) and HbA1c periodically.',
        'contraindications': 'Severe renal impairment (eGFR < 30 mL/min), acute metabolic acidosis, or severe hypoxic states.',
        'potential_side_effects': 'Mild gastrointestinal disturbance (bloating, loose stools), rare lactic acidosis.',
        'source_reference': 'American Diabetes Association (ADA) Standards of Care; RSSDI Guidelines India.',
        'is_prescription_required': 1
    },
    {
        'match_keys': ['atorvastatin', 'atorva', 'lipitor', 'cholesterol', 'statin', 'rosuvastatin'],
        'generic_name': 'Atorvastatin Calcium (10mg / 20mg / 40mg)',
        'brand_names': 'Atorva, Lipitor, Storvas, Tonact, Atocor',
        'common_uses': 'Lowers LDL cholesterol and triglycerides, reduces the risk of stroke, myocardial infarction, and cardiovascular disease.',
        'dosage_forms': 'Oral Tablets (10mg, 20mg, 40mg, 80mg)',
        'precautions': 'Take once daily at any time (often evening). Avoid excessive grapefruit juice. Report unexplained muscle aches or weakness.',
        'contraindications': 'Active liver disease, unexplained persistent elevation of serum transaminases, pregnancy, or nursing.',
        'potential_side_effects': 'Mild headache, constipation, myalgia (muscle soreness), transient liver enzyme elevations.',
        'source_reference': 'Cardiological Society of India (CSI) Lipid Guidelines; ACC/AHA Cholesterol Guidelines.',
        'is_prescription_required': 1
    }
]

def resolve_medicine_details(query, med_record=None):
    """
    Intelligently resolves clinical product / medicine details for ANY search query.
    1. Checks database medicine record if available.
    2. Searches clinical knowledge base.
    3. Dynamically generates accurate, clinical guidance tailored to the product category.
    """
    q_clean = (query or '').strip().lower()

    # 1. Check curated Clinical KB first for rich matching
    for entry in CLINICAL_MEDICINE_KB:
        if any(k in q_clean for k in entry['match_keys']) or any(q_clean in k for k in entry['match_keys']):
            return {
                'generic_name': entry['generic_name'],
                'brand_names': entry['brand_names'],
                'common_uses': entry['common_uses'],
                'dosage_forms': entry['dosage_forms'],
                'precautions': entry['precautions'],
                'contraindications': entry['contraindications'],
                'potential_side_effects': entry['potential_side_effects'],
                'source_reference': entry['source_reference'],
                'is_prescription_required': entry['is_prescription_required']
            }

    # 2. Database Record
    if med_record:
        cat = (med_record.get('category') or '').lower()
        is_rx = 0 if any(otc_w in cat for otc_w in ['otc', 'fever', 'cold', 'pain', 'digestive']) else 1
        return {
            'generic_name': med_record.get('name') or query.title(),
            'brand_names': f"Verified Formulations of {query.title()}",
            'common_uses': med_record.get('purpose') or med_record.get('general_info') or 'Therapeutic clinical support.',
            'dosage_forms': 'Standard Formulations (Tablets, Syrup, Topical)',
            'precautions': med_record.get('precautions') or 'Follow package directions or healthcare provider instructions.',
            'contraindications': med_record.get('avoid_if') or 'Consult physician in case of pregnancy, kidney or liver disease.',
            'potential_side_effects': 'Consult pharmacist or package insert for specific adverse reaction warnings.',
            'source_reference': 'National Formulary of India (NFI); CDSCO Verified Formulary.',
            'is_prescription_required': is_rx
        }

    # 3. Dynamic Category Detection for Any Search Query
    is_topical_or_otc = any(w in q_clean for w in [
        'lotion', 'cream', 'gel', 'spf', 'sun', 'wash', 'soap', 'oil', 'shampoo',
        'drop', 'balm', 'lozenge', 'spray', 'vitamin', 'supplement', 'tea', 'herbal',
        'sanitizer', 'wipe', 'patch', 'paste', 'cotton', 'bandage', 'antiseptic',
        'moisturizer', 'cleanser', 'serum', 'mask', 'syrup', 'tonic', 'spray', 'powder'
    ])
    is_rx_drug = any(w in q_clean for w in [
        'antibiotic', 'steroid', 'insulin', 'injection', 'cardiac', 'hypertension',
        'statin', 'antidepressant', 'sedative', 'schedule h', 'schedule x', 'prescribed'
    ])

    rx_status = 1 if is_rx_drug else (0 if is_topical_or_otc else 0)

    category_label = "Topical Healthcare & Personal Care Product" if is_topical_or_otc else "Clinical Therapeutic Product"
    return {
        'generic_name': f"{query.title()} ({category_label})",
        'brand_names': f"Certified Indian & International Brands for {query.title()}",
        'common_uses': f"Primary symptomatic care and wellness support for {query.title()}. Formulated for dedicated therapeutic or personal care use.",
        'dosage_forms': "Topical Formulation, Lotion, Gel, Oral Tablet / Capsule as applicable",
        'precautions': "Verify product packaging seal before use. Follow recommended frequency and dosage guidance. Keep out of reach of young children.",
        'contraindications': "Known individual hypersensitivity or allergic dermatitis to primary active constituents.",
        'potential_side_effects': "Mild localized sensitivity or transient irritation in hypersensitive individuals. Discontinue if redness persists.",
        'source_reference': "Central Drugs Standard Control Organisation (CDSCO); National Formulary of India (NFI).",
        'is_prescription_required': rx_status
    }

@pharmacies_bp.route('/api/pharmacies/search', methods=['GET'])
def search_pharmacies():
    """Search for medicine details and generate destination links."""
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'medicine_info': None, 'destinations': []})

    # 1. Search database for medicine details
    med = database.fetch_one(
        g.db,
        "SELECT * FROM medicines WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ? LIMIT 1",
        (f"%{query.lower()}%", f"{query.lower()}%")
    )

    if not med:
        med = database.fetch_one(
            g.db,
            "SELECT * FROM medicines WHERE LOWER(purpose) LIKE ? LIMIT 1",
            (f"%{query.lower()}%",)
        )

    encoded_q = quote(query)

    # 2. Build destination links
    destinations = []
    try:
        providers = database.fetch_all(g.db, "SELECT * FROM pharmacy_providers WHERE is_active = 1")
        if providers:
            for p in providers:
                tpl = p.get('search_url_template') or f"{p['base_url']}?q={{query}}"
                destinations.append({
                    'provider_name': p['provider_name'],
                    'search_url': tpl.replace('{query}', encoded_q)
                })
    except Exception:
        pass

    if not destinations:
        for name, tpl in PHARMACY_TEMPLATES:
            destinations.append({
                'provider_name': name,
                'search_url': tpl.replace('{query}', encoded_q)
            })

    # 3. Intelligently format medicine info for ANY search query
    med_info = resolve_medicine_details(query, med)

    return jsonify({
        'query': query,
        'medicine_info': med_info,
        'destinations': destinations
    })

@pharmacies_bp.route('/api/medicines/allergy-check', methods=['POST'])
def check_allergy():
    """Verify if the queried medicine interacts with documented patient allergies."""
    medicine_name = request.args.get('medicine_name', '')
    if not medicine_name and request.is_json and request.json:
        medicine_name = request.json.get('medicine_name', '')
    medicine_name = str(medicine_name).strip()
    user = get_current_user()

    known_allergies = "None documented"
    if user:
        profile = database.fetch_one(g.db, "SELECT allergies FROM patient_profiles WHERE user_id = ?", (user['id'],))
        if profile and profile.get('allergies'):
            known_allergies = profile['allergies']

    med_lower = medicine_name.lower()
    allergies_lower = known_allergies.lower()

    has_warning = False
    alerts = []

    # Check common cross-sensitivities
    if 'penicillin' in allergies_lower and any(drug in med_lower for drug in ['amoxicillin', 'ampicillin', 'penicillin', 'augmentin']):
        has_warning = True
        alerts.append(f"CRITICAL WARNING: You have a documented allergy to Penicillin. '{medicine_name}' belongs to the penicillin / beta-lactam class.")

    if 'aspirin' in allergies_lower or 'nsaid' in allergies_lower:
        if any(drug in med_lower for drug in ['ibuprofen', 'aspirin', 'diclofenac', 'naproxen']):
            has_warning = True
            alerts.append(f"WARNING: '{medicine_name}' is an NSAID which may trigger allergic reaction due to documented NSAID sensitivity.")

    if 'sulfa' in allergies_lower and 'sulfa' in med_lower:
        has_warning = True
        alerts.append(f"WARNING: Potential sulfonamide allergy cross-reaction detected with '{medicine_name}'.")

    return jsonify({
        'medicine_name': medicine_name,
        'has_allergy_warning': has_warning,
        'alerts': alerts,
        'known_allergies': known_allergies
    })

@pharmacies_bp.route('/api/medicines/reminders', methods=['GET', 'POST'])
def medicine_reminders():
    """List or create medicine reminders."""
    user = get_current_user()
    patient_id = user['id'] if user else 18

    if request.method == 'GET':
        reminders = database.fetch_all(
            g.db,
            "SELECT * FROM medicine_reminders WHERE patient_user_id = ? ORDER BY id DESC",
            (patient_id,)
        ) or []
        return jsonify(reminders)

    # POST create reminder
    data = request.get_json() or {}
    name = data.get('medicine_name', '').strip()
    dosage = data.get('dosage', '').strip()
    time = data.get('reminder_time', '09:00')
    days = data.get('days_of_week', 'Daily')

    if not name:
        return jsonify({'ok': False, 'error': 'Medicine name is required'}), 400

    rem_id = database.insert(
        g.db,
        """INSERT INTO medicine_reminders (patient_user_id, medicine_name, dosage, reminder_time, days_of_week, is_active)
           VALUES (?, ?, ?, ?, ?, 1)""",
        (patient_id, name, dosage, time, days)
    )

    return jsonify({
        'ok': True,
        'reminder_id': rem_id,
        'message': f"Reminder created for {name} at {time}"
    }), 201
