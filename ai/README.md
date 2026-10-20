# AI Engine & Clinical Safety Layer — AI Health Clinic

## Purpose
The `ai/` directory provides the medical consultation reasoning, clinical emergency red-flag screening, grounded lab report summarization, and medical source retrieval subsystems.

## Key Subsystems
1. `safety_rules/emergency_rules.py`:
   - Independent safety rule layer that scans patient messages for life-threatening medical conditions (severe chest pain, stroke FAST symptoms, acute dyspnea, anaphylaxis, severe trauma) before any language model generation.
   - Provides immediate emergency response guidance (dialing 112 / 108 / 102).
2. `health_assistant/assistant.py`:
   - Conversational assistant supporting multi-turn dialogue, clarifying questions, cautious advice, and multi-lingual input (English, Hindi, Hinglish).
   - Returns structured consultation summaries matching Image Screen 3 (reported symptoms, possible causes, general guidance, and verified source citations).
3. `medical_retrieval/sources.py`:
   - Curated medical references linking to official health organizations (NHS UK, Mayo Clinic, WHO).
4. `report_summarization/summarizer.py`:
   - Deterministic lab value extractor and summarizer. Extracts numerical values (Hemoglobin, Platelets, WBC, Fasting Glucose, Vitamin D, Creatinine), assesses against standard reference ranges, and formulates patient-friendly explanations without inventing missing data.

## Configuration
Controlled via `.env`:
- `AI_PROVIDER=local_rule_engine` (Offline grounded medical engine, default)
- `AI_PROVIDER=gemini` (Google Gemini API via `GEMINI_API_KEY`)
- `AI_PROVIDER=ollama` (Local LLM via `OLLAMA_BASE_URL`)
