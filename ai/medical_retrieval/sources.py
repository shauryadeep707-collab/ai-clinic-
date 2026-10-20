"""
Medical Knowledge Retrieval and Source Grounding
Provides verified medical references from NHS, Mayo Clinic, and WHO.
"""

CURATED_SOURCES = {
    "headache": {
        "title": "Tension-type and Primary Headaches",
        "sources": [
            {"name": "NHS Guidelines", "url": "https://www.nhs.uk/conditions/headaches/"},
            {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/diseases-conditions/tension-headache/symptoms-causes/syc-20353977"}
        ],
        "possible_causes": ["Tension headache", "Dehydration or eye strain", "Migraine", "Lack of sleep / stress"],
        "guidance": "Rest in a quiet, dark room, hydrate with water, and avoid bright screens. Consult a doctor if the headache is unusually severe or accompanied by fever/stiff neck."
    },
    "fever": {
        "title": "Fever & Viral Illness Management",
        "sources": [
            {"name": "WHO Guidelines", "url": "https://www.who.int/news-room/fact-sheets/detail/fever"},
            {"name": "NHS Guidelines", "url": "https://www.nhs.uk/conditions/fever-in-adults/"}
        ],
        "possible_causes": ["Seasonal viral infection", "Bacterial respiratory infection", "Urinary tract infection"],
        "guidance": "Monitor temperature periodically, maintain fluid intake, and rest. Seek clinical medical attention if fever exceeds 102°F (38.9°C) or lasts more than 3 days."
    },
    "cough": {
        "title": "Acute Cough & Respiratory Symptoms",
        "sources": [
            {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/symptoms/cough/basics/definition/sym-20050846"},
            {"name": "NHS Guidelines", "url": "https://www.nhs.uk/conditions/cough/"}
        ],
        "possible_causes": ["Upper respiratory viral infection", "Post-nasal drip / Allergy", "Bronchitis", "Acid reflux"],
        "guidance": "Stay hydrated with warm liquids, consider honey for throat soothing (adults only), and avoid environmental smoke. Consult a doctor if coughing up blood or experiencing breathing difficulty."
    },
    "stomach": {
        "title": "Abdominal Discomfort & Gastritis",
        "sources": [
            {"name": "NHS Guidelines", "url": "https://www.nhs.uk/conditions/stomach-ache/"},
            {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/diseases-conditions/gastritis/symptoms-causes/syc-20355807"}
        ],
        "possible_causes": ["Indigestion / Gastritis", "Mild foodborne illness", "Irritable bowel", "Dehydration"],
        "guidance": "Eat light, non-spicy meals (BRAT diet: bananas, rice, applesauce, toast) and take small sips of oral rehydration fluids. Consult a doctor if pain is sharp and localized or accompanied by vomiting."
    }
}

def retrieve_guidance(query: str):
    q = query.lower()
    for key, data in CURATED_SOURCES.items():
        if key in q:
            return data
    # General fallback
    return {
        "title": "General Health Guidance",
        "sources": [
            {"name": "NHS Health A to Z", "url": "https://www.nhs.uk/conditions/"},
            {"name": "Mayo Clinic Symptom Checker", "url": "https://www.mayoclinic.org/symptom-checker/select-symptom/itt-20088540"}
        ],
        "possible_causes": ["General physiological response", "Lifestyle or fatigue factors", "Needs doctor assessment"],
        "guidance": "Monitor your symptoms closely, ensure adequate rest and hydration, and consult a qualified healthcare professional for formal diagnosis."
    }
