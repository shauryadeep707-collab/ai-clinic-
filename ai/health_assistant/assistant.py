import logging
from typing import Dict, Any, List
from ai.safety_rules.emergency_rules import evaluate_emergency_red_flags
from ai.medical_retrieval.sources import retrieve_guidance
from backend.app.config.settings import settings

logger = logging.getLogger("ai_health_clinic.ai_assistant")

class AIHealthAssistant:
    def __init__(self):
        self.provider = settings.AI_PROVIDER

    def generate_consultation_reply(self, conversation_history: List[Dict[str, str]], patient_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes conversation and returns structured clinical response matching Image Screen 3.
        """
        last_user_message = ""
        for msg in reversed(conversation_history):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        # 1. Independent Emergency Safety Check
        is_emergency, urgent_text = evaluate_emergency_red_flags(last_user_message)
        if is_emergency:
            return {
                "reply": urgent_text,
                "is_urgent_warning": 1,
                "triage_level": "Emergency",
                "reported_symptoms": [last_user_message[:50] + "..."],
                "possible_causes": ["Acute medical condition requiring immediate emergency evaluation"],
                "general_guidance": "Do not wait. Seek urgent clinical care or call emergency helpline immediately.",
                "medical_sources": [
                    {"name": "Emergency Medical Protocols", "url": "https://www.who.int/emergencies"}
                ]
            }

        # 2. Retrieve verified medical source data
        retrieval = retrieve_guidance(last_user_message)
        
        # 3. Check for language (Hindi / Hinglish vs English)
        is_hinglish = any(w in last_user_message.lower() for w in ["dard", "saans", "bukhar", "khansi", "pet", "sar", "sir"])
        
        # 4. Formulate cautious response
        if is_hinglish:
            reply_text = (
                f"Maine aapke lakshan samjhe: '{last_user_message}'.\n\n"
                f"Kripya dhyan dein:\n"
                f"• {retrieval['guidance']}\n"
                f"• Agar dard ya takleef 48 ghante se zyada rahe ya aur badhe, to turant doctor se consult karein.\n"
                f"• Paani pijiye aur paryapt aaraam karein."
            )
        else:
            if len(conversation_history) <= 2:
                # First or second turn: ask clarifying questions as in Screen 3
                reply_text = (
                    f"I understand you are experiencing: '{last_user_message}'.\n\n"
                    f"To help provide relevant general information, could you share:\n"
                    f"1. How long have you had this symptom, and did it start suddenly or gradually?\n"
                    f"2. On a scale of 1 to 10, how severe is the discomfort?\n"
                    f"3. Are you experiencing any other symptoms such as fever, nausea, dizziness, or shortness of breath?\n\n"
                    f"General initial advice: {retrieval['guidance']}"
                )
            else:
                reply_text = (
                    f"Thank you for the additional context. Based on your symptoms and clinical guidelines:\n\n"
                    f"• {retrieval['guidance']}\n"
                    f"• Monitor for any red-flag signs such as high fever, severe dizziness, or breathing difficulties.\n"
                    f"• If symptoms persist for more than 48 hours or worsen, please schedule an appointment with a verified clinician."
                )

        return {
            "reply": reply_text,
            "is_urgent_warning": 0,
            "triage_level": "Routine",
            "reported_symptoms": [last_user_message.strip()],
            "possible_causes": retrieval["possible_causes"],
            "general_guidance": retrieval["guidance"],
            "medical_sources": retrieval["sources"]
        }

assistant_instance = AIHealthAssistant()

def get_assistant() -> AIHealthAssistant:
    return assistant_instance
