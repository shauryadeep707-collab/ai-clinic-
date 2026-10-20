import re
from typing import Tuple, Optional

# Clinical Red-Flag Keywords and Patterns
EMERGENCY_PATTERNS = [
    # Cardiac / Angina / Infarction
    r"(severe\s+chest\s+pain|crushing\s+chest\s+pain|pain\s+radiating\s+to\s+(left\s+arm|jaw|back)|chest\s+pressure|heart\s+attack)",
    # Stroke / Cerebrovascular (FAST)
    r"(sudden\s+weakness|facial\s+droop|slurred\s+speech|can't\s+move\s+(arm|leg)|sudden\s+loss\s+of\s+vision|paralysis)",
    # Respiratory Distress
    r"(cannot\s+breathe|gasping\s+for\s+air|severe\s+shortness\s+of\s+breath|blue\s+lips|stridor|choking)",
    # Anaphylaxis / Severe Allergy
    r"(throat\s+closing|tongue\s+swelling|anaphylaxis|swollen\s+lips\s+and\s+breathing\s+difficulty)",
    # Severe Trauma / Neurological / Bleeding
    r"(unconscious|unresponsive|heavy\s+bleeding|vomiting\s+blood|coughing\s+blood|seizure|head\s+injury\s+and\s+vomiting)",
    # Hindi / Hinglish Emergency Signs
    r"(seene\s+mein\s+(tez\s+)?dard|saans\s+nahi\s+aa\s+rahi|khoon\s+ki\s+ulti|behosh|lakwa)"
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in EMERGENCY_PATTERNS]

def evaluate_emergency_red_flags(user_message: str) -> Tuple[bool, Optional[str]]:
    """
    Independent Safety Rule Layer:
    Scans patient inputs for clinical emergency warning signs BEFORE passing to generative AI.
    Returns (is_emergency: bool, urgent_guidance_text: Optional[str]).
    """
    for pattern in COMPILED_PATTERNS:
        if pattern.search(user_message):
            return True, (
                "⚠️ CRITICAL EMERGENCY WARNING:\n\n"
                "Your symptoms indicate a potential medical emergency that requires immediate clinical intervention.\n\n"
                "• Call emergency services immediately: Call 112 (National Emergency), 108 / 102 (Ambulance), or your local hospital emergency room.\n"
                "• Do NOT drive yourself to the hospital.\n"
                "• If someone is with you, notify them immediately.\n"
                "• If experiencing chest pain, sit down and remain calm while emergency assistance is en route.\n\n"
                "Clinical Disclaimer: This AI assistant is not an emergency response dispatch service."
            )
    return False, None
