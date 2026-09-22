"""AI prompts and system instructions for medical safety."""

def get_system_prompt() -> str:
    """
    Get the system prompt for AI with medical safety instructions.
    """
    return """You are a clinical decision support AI assistant for a healthcare system. Your role is to help organize medical information and provide decision support, NOT to replace qualified healthcare professionals.

CRITICAL SAFETY RULES:
1. NEVER claim certainty when evidence is uncertain
2. NEVER present yourself as a doctor or medical professional
3. NEVER independently prescribe medication or tell patients to stop/change medication
4. NEVER tell a patient to replace professional medical care
5. ALWAYS identify emergency warning signs when present
6. ALWAYS encourage urgent professional care when appropriate
7. ALWAYS distinguish medical information from diagnosis
8. ALWAYS explain uncertainty in your assessments
9. ALWAYS avoid unsupported medical claims
10. ALWAYS cite retrieved sources when available
11. ALWAYS ask follow-up questions when information is insufficient
12. ALWAYS consider allergies and medication history when relevant
13. NEVER invent medications, dosages, medical guidelines, or sources

YOUR ROLE:
- Help organize patient symptoms and medical information
- Retrieve information from approved medical sources
- Present structured suggestions for healthcare professional review
- Identify potential warning signs and urgency levels
- Ask appropriate follow-up questions to gather necessary information
- Provide citations to medical sources when available

OUTPUT FORMAT:
Always provide structured, JSON-formatted responses with clear sections for symptoms, possible conditions, warning signs, urgency level, and recommendations.

Remember: This is decision-support information only. Qualified healthcare professionals remain responsible for final diagnosis, prescription, and treatment decisions."""


def get_assessment_prompt(
    patient_input: str,
    patient_history: dict = None,
    current_medications: list = None
) -> str:
    """
    Get the assessment prompt for analyzing patient symptoms.
    
    Args:
        patient_input: Patient's description of symptoms
        patient_history: Patient's medical history
        current_medications: List of current medications
    
    Returns:
        Formatted prompt for AI assessment
    """
    prompt = f"""Analyze the following patient information and provide a structured medical assessment.

PATIENT INPUT:
{patient_input}
"""

    if patient_history:
        prompt += f"""
PATIENT MEDICAL HISTORY:
{json.dumps(patient_history, indent=2)}
"""

    if current_medications:
        prompt += f"""
CURRENT MEDICATIONS:
{', '.join(current_medications)}
"""

    prompt += """
REQUIRED OUTPUT FORMAT (JSON):
{
    "symptoms_identified": ["symptom1", "symptom2"],
    "follow_up_questions": ["question1", "question2", "question3"],
    "possible_conditions": [
        {
            "name": "condition name",
            "likelihood": "low/medium/high",
            "description": "brief description"
        }
    ],
    "warning_signs": ["warning1", "warning2"],
    "urgency_level": "INFORMATIONAL/ROUTINE_CONSULTATION/PROMPT_MEDICAL_REVIEW/URGENT_MEDICAL_ATTENTION",
    "general_information": "explanation in simple language",
    "medication_information": [],
    "recommended_next_step": "clear recommendation",
    "sources": [{"name": "source", "url": "url", "title": "title"}],
    "confidence": 0.0-1.0
}

Remember to follow all safety rules and never provide definitive diagnoses or prescriptions."""

    return prompt


def get_follow_up_prompt(
    consultation_context: dict,
    current_symptoms: list,
    previous_questions: list = None
) -> str:
    """
    Get the prompt for generating follow-up questions.
    
    Args:
        consultation_context: Current consultation information
        current_symptoms: Symptoms already identified
        previous_questions: Questions already asked
    
    Returns:
        Formatted prompt for follow-up question generation
    """
    prompt = f"""Generate 2-3 relevant follow-up questions to gather more information.

CURRENT SYMPTOMS IDENTIFIED:
{', '.join(current_symptoms)}
"""

    if previous_questions:
        prompt += f"""
PREVIOUS QUESTIONS ASKED:
{', '.join(previous_questions)}
"""

    prompt += """
INSTRUCTIONS:
- Ask questions that will help clarify the symptoms
- Avoid asking about information already provided
- Focus on duration, severity, location, and aggravating/relieving factors
- Ask about related symptoms that might be relevant
- Maximum 3 questions

OUTPUT FORMAT (JSON):
{
    "questions": ["question1", "question2", "question3"]
}"""

    return prompt