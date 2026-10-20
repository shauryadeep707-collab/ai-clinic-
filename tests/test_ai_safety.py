import pytest
from ai.safety_rules.emergency_rules import evaluate_emergency_red_flags
from ai.health_assistant.assistant import get_assistant

def test_emergency_red_flags_cardiac():
    is_emergency, warning = evaluate_emergency_red_flags("I have severe crushing chest pain radiating to left arm")
    assert is_emergency is True
    assert "CRITICAL EMERGENCY WARNING" in warning
    assert "112" in warning

def test_emergency_red_flags_stroke():
    is_emergency, warning = evaluate_emergency_red_flags("Sudden weakness on one side and slurred speech")
    assert is_emergency is True
    assert "CRITICAL EMERGENCY WARNING" in warning

def test_emergency_red_flags_hindi():
    is_emergency, warning = evaluate_emergency_red_flags("Mujhe seene mein tez dard ho raha hai")
    assert is_emergency is True
    assert "CRITICAL EMERGENCY WARNING" in warning

def test_routine_symptom_cautious_triage():
    assistant = get_assistant()
    reply = assistant.generate_consultation_reply([
        {"role": "user", "content": "I have had a mild headache since yesterday"}
    ])
    assert reply["is_urgent_warning"] == 0
    assert reply["triage_level"] == "Routine"
    assert len(reply["medical_sources"]) > 0
    assert any("NHS" in s["name"] or "Mayo" in s["name"] for s in reply["medical_sources"])
