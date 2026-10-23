"""AI Service for medical assessments and consultations."""

import logging
from typing import Any, Dict, List, Optional

from django.conf import settings

from core.constants import UrgencyLevel
from core.exceptions import AIServiceError, AIResponseTruncatedError
from knowledge.services import RetrievalService

from ..providers import get_llm_provider
from .prompts import (
    get_chat_system_prompt,
    get_professional_system_prompt,
    get_document_analysis_system_prompt,
)

logger = logging.getLogger(__name__)

CONVERSATION_SCHEMA = {
    "reply": (
        "the full detailed answer to the patient (roughly 150-300 words for clinical queries, "
        "~350 when several serious differentials apply), explaining what it could mean, why it "
        "happens, what to do safely, what to watch for, and follow-up questions; blank-line-separated "
        "sections with short plain-text labels, \"- \" bullets, inline [1] citations, NO markdown"
    ),
    "symptoms_identified": ["symptom the patient reported"],
    "follow_up_questions": ["question to ask the patient (max 3, never repeat answered ones)"],
    "possible_conditions": [
        {
            "name": "condition name",
            "likelihood": "low | medium | high",
            "description": "detailed clinical explanation grounded in the evidence of why this condition fits the patient's presentation",
        }
    ],
    "warning_signs": ["emergency warning sign present"],
    "urgency_level": (
        "one of INFORMATIONAL, ROUTINE_CONSULTATION, PROMPT_MEDICAL_REVIEW, "
        "URGENT_MEDICAL_ATTENTION"
    ),
    "general_information": "comprehensive educational background and plain-language explanation grounded in the evidence",
    "recommended_next_step": "clear, detailed, and actionable next step for the patient",
}

PROFESSIONAL_SCHEMA = {
    "reply": (
        "the full clinician-level analysis (roughly 200-350 words of rigorous plain text): ranked "
        "differentials with discriminating features, mechanism, what the evidence says with [n] "
        "citations, workup, dosing and interaction considerations, red flags, and gaps; "
        "blank-line-separated sections with short plain-text labels, \"- \" bullets, inline [1] "
        "citations, NO markdown"
    ),
    "symptoms_identified": ["symptom or clinical finding mentioned in the case"],
    "follow_up_questions": [
        "missing case information that would refine the answer (max 3)"
    ],
    "possible_conditions": [
        {
            "name": "condition name",
            "likelihood": "low | medium | high",
            "description": "detailed clinical rationale with evidence grounding, pathophysiology, and probability context",
        }
    ],
    "warning_signs": ["red flags, contraindications, or dangerous interactions present"],
    "urgency_level": (
        "one of INFORMATIONAL, ROUTINE_CONSULTATION, PROMPT_MEDICAL_REVIEW, "
        "URGENT_MEDICAL_ATTENTION"
    ),
    "general_information": "detailed clinical summary and guideline review grounded in the evidence",
    "recommended_next_step": "suggested next step for the clinician",
}

DOCUMENT_ANALYSIS_SCHEMA = {
    "reply": "thorough clinical explanation of the document/scan findings, explaining what each finding means in context and outlining evidence-based clinical steps",
    "document_category": "imaging_scan | lab_result | pathology | discharge_summary | prescription | general",
    "exam_type": "detected exam name or modality (e.g. Chest CT with contrast)",
    "document_summary": "detailed clinical summary of the scan / lab study findings and impressions",
    "scan_findings": [
        {
            "area": "anatomical area or analyte name",
            "finding": "description of observation",
            "is_abnormal": False
        }
    ],
    "abnormalities": ["specific abnormal or concerning findings highlighted"],
    "possible_conditions": [
        {
            "name": "condition name",
            "likelihood": "low | medium | high",
            "description": "detailed clinical rationale grounded in evidence",
        }
    ],
    "warning_signs": ["emergency red flags detected requiring urgent evaluation"],
    "urgency_level": (
        "one of INFORMATIONAL, ROUTINE_CONSULTATION, PROMPT_MEDICAL_REVIEW, "
        "URGENT_MEDICAL_ATTENTION"
    ),
    "trusted_solutions": [
        {
            "action": "recommended clinical action or management step",
            "guideline_source": "e.g. Fleischner Society / WHO / NIH",
            "details": "explanation of rationale"
        }
    ],
    "recommended_next_step": "clear actionable next step for the patient or clinician",
}

_VALID_LIKELIHOODS = {"low", "medium", "high"}

_KINYARWANDA_KEYWORDS = {
    "mfite", "umuriro", "umutwe", "urampandura", "kandi", "uwo", "mubyiza",
    "muguhumeka", "ububabare", "umunaniro", "gutema", "kugira", "ntabwo",
    "ibimenyetso", "urashaka", "urwaye", "mugira", "ndagize", "ndumva", "muri",
    "nagize", "inkorora", "kuva", "minsi", "naranze", "nshobora",
    "ndwaye", "ariko", "muraho", "mwiriwe", "murakoze", "mwaramutse", "byihuse",
    "nubwo", "ndabona", "nahuye", "nka", "mugongo", "mbabara", "ndababara",
    "nda", "naniwe", "kinyarwanda", "rwanda", "ikibazo", "inyandiko", "ubuzima",
    "uburyo", "umwana", "indwara", "imiti", "umuganga", "farumasi", "kuruka",
    "impiswi", "gucibwamo", "kuribwa", "isukari", "umuvuduko", "igifu", "akaga",
    "amaraso", "amasaha", "ibyumweru", "ejo", "nza", "ndashaka",
    "nakoresha", "bigabanuke", "gugabanuka", "kugabanuka", "iki", "ngo", "nte",
    "mbigenze", "nakora", "nyabuneka", "mubwire", "nsubiza", "subiza", "bita",
    "amatsiko", "gute", "ryari", "he", "se", "yego", "oya", "ubwo", "hafi",
    "wanjye", "yawe", "yacu", "yanyu", "wacu", "wanyu", "cyanjye", "byanjye",
    "ufite", "bafite", "gufata", "wafashe", "bafashe", "umuti", "kwivuza",
    "gukira", "kwitonda", "ibipimo", "isuka", "ikizagabanya"
}


class AIService:
    """Service for AI-powered medical conversations and assessments."""

    MAX_HISTORY_MESSAGES = 20
    # 8 ranked passages rather than 6: the approved corpus is only 38 documents of
    # 241-995 characters each (measured), so a 6-passage window routinely left the
    # model with ~1.5 passages that actually matched the question. Retrieval caps
    # the prompt at roughly 8 x 995 chars of content, which is affordable.
    MAX_EVIDENCE_RESULTS = 8

    def __init__(self):
        self.provider_name = settings.AI_PROVIDER
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        self.base_url = getattr(settings, "AI_BASE_URL", "")
        self.timeout = getattr(settings, "AI_REQUEST_TIMEOUT", 60)
        self.retrieval_service = RetrievalService()

    def converse(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        patient_history: Optional[Dict] = None,
        current_medications: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Continue a conversation with a patient.

        Searches all approved medical sources for evidence relevant to the
        conversation, then lets the configured LLM reply using that evidence.
        Falls back to a deterministic conversational reply when no LLM
        provider/key is configured or when the provider call fails.

        Args:
            message: The patient's latest message
            history: Previous turns as [{"role": "user"|"assistant", "content": ...}]
            patient_history: Patient's medical history
            current_medications: List of current medications

        Returns:
            Structured reply with follow-up questions and cited sources
        """
        sanitized_history = self._sanitize_history(history)
        language = self._detect_language(message, sanitized_history)
        if self._is_general_greeting(message):
            return self._greeting_result(language)
        if self._is_incomplete_message(message):
            return self._clarification_result(language)

        query = self._build_query(sanitized_history, message)
        evidence = self._retrieve_evidence(query)

        if not self._use_llm_provider():
            return self._mock_conversation(
                message, sanitized_history, patient_history, current_medications, evidence
            )

        try:
            messages = self._build_messages(
                message, sanitized_history, patient_history, current_medications, evidence, language
            )
            provider = get_llm_provider(
                self.provider_name,
                api_key=self.api_key,
                model=self.model,
                base_url=self.base_url,
            )
            raw = provider.complete_structured(messages, CONVERSATION_SCHEMA)
            return self._normalize_result(raw, evidence)
        except AIResponseTruncatedError as exc:
            # Loud on purpose: a clipped long answer must be distinguishable from a
            # provider outage, otherwise every depth change looks like a prompt bug.
            logger.error(
                "LLM reply hit the completion budget and was truncated; using fallback "
                "conversation. %s",
                exc,
            )
            return self._mock_conversation(
                message, sanitized_history, patient_history, current_medications, evidence
            )
        except AIServiceError as exc:
            logger.warning("LLM provider failed, using fallback conversation: %s", exc)
            return self._mock_conversation(
                message, sanitized_history, patient_history, current_medications, evidence
            )

    def converse_professional(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        professional_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Continue a decision-support conversation with a clinician.

        Searches all approved medical sources for evidence relevant to the
        conversation, then lets the configured LLM answer at clinician level
        using that evidence. Falls back to a deterministic source-excerpt
        reply when no LLM provider/key is configured or on provider failure.

        Args:
            message: The clinician's latest message
            history: Previous turns as [{"role": "user"|"assistant", "content": ...}]
            professional_context: Optional case details supplied by the clinician

        Returns:
            Structured reply with follow-up questions and cited sources
        """
        sanitized_history = self._sanitize_history(history)
        language = self._detect_language(message, sanitized_history)
        if self._is_general_greeting(message):
            return self._greeting_result(language, professional=True)

        query = self._build_query(sanitized_history, message)
        evidence = self._retrieve_evidence(query)

        if not self._use_llm_provider():
            return self._mock_professional_conversation(
                message, sanitized_history, evidence
            )

        try:
            messages = self._build_professional_messages(
                message, sanitized_history, professional_context, evidence, language
            )
            provider = get_llm_provider(
                self.provider_name,
                api_key=self.api_key,
                model=self.model,
                base_url=self.base_url,
            )
            raw = provider.complete_structured(messages, PROFESSIONAL_SCHEMA)
            return self._normalize_result(raw, evidence)
        except AIResponseTruncatedError as exc:
            logger.error(
                "LLM professional reply hit the completion budget and was truncated; "
                "using fallback reply. %s",
                exc,
            )
            return self._mock_professional_conversation(
                message, sanitized_history, evidence, fallback_reason=str(exc)
            )
        except AIServiceError as exc:
            logger.warning(
                "LLM provider failed, using fallback professional reply: %s", exc
            )
            return self._mock_professional_conversation(
                message, sanitized_history, evidence, fallback_reason=str(exc)
            )

    def analyze_medical_document(
        self,
        document_text: str,
        document_category: str = "imaging_scan",
        exam_type: str = "",
        user_message: str = "",
        user_role: str = "PATIENT",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Perform deep clinical analysis on an uploaded medical document / scan report.

        Args:
            document_text: Extracted plain text or structured notes from document
            document_category: Detected category (imaging_scan, lab_result, etc.)
            exam_type: Inferred modality / study title (e.g. Chest CT with contrast)
            user_message: Optional prompt or question from the user
            user_role: Role of the uploading user (PATIENT, DOCTOR, PHARMACIST)
            history: Optional conversation history

        Returns:
            Structured clinical report analysis with findings, abnormalities,
            urgency, possible conditions, trusted solutions, and citations.
        """
        sanitized_history = self._sanitize_history(history)
        corpus_for_lang = f"{user_message} {document_text[:500]}"
        language = self._detect_language(corpus_for_lang, sanitized_history)

        query = self._build_document_query(exam_type, document_category, document_text, user_message)
        evidence = self._retrieve_evidence(query)

        if not self._use_llm_provider():
            return self._mock_document_analysis(
                document_text=document_text,
                document_category=document_category,
                exam_type=exam_type,
                user_message=user_message,
                user_role=user_role,
                evidence=evidence,
                language=language,
            )

        try:
            evidence_block = self.retrieval_service.format_evidence_for_ai(evidence)
            system_prompt = get_document_analysis_system_prompt(
                evidence_block=evidence_block,
                document_category=document_category,
                exam_type=exam_type,
                language=language,
                user_role=user_role,
            )

            prompt_user_content = (
                f"DOCUMENT TITLE / STUDY: {exam_type}\n"
                f"DOCUMENT CATEGORY: {document_category}\n"
                f"USER QUESTION: {user_message or 'Please analyze this medical report/scan in detail, flag any abnormalities, and provide trusted clinical solutions and next steps.'}\n\n"
                f"--- EXTRACTED REPORT CONTENT ---\n"
                f"{document_text[:12000]}"
            )

            messages = [
                {"role": "system", "content": system_prompt},
                *sanitized_history,
                {"role": "user", "content": prompt_user_content},
            ]

            provider = get_llm_provider(
                self.provider_name,
                api_key=self.api_key,
                model=self.model,
                base_url=self.base_url,
            )
            raw = provider.complete_structured(messages, DOCUMENT_ANALYSIS_SCHEMA)
            return self._normalize_document_result(raw, evidence, document_category, exam_type)
        except AIResponseTruncatedError as exc:
            logger.error(
                "LLM document analysis hit the completion budget and was truncated; "
                "using fallback. %s",
                exc,
            )
            return self._mock_document_analysis(
                document_text=document_text,
                document_category=document_category,
                exam_type=exam_type,
                user_message=user_message,
                user_role=user_role,
                evidence=evidence,
                language=language,
            )
        except AIServiceError as exc:
            logger.warning("LLM document analysis failed, using fallback: %s", exc)
            return self._mock_document_analysis(
                document_text=document_text,
                document_category=document_category,
                exam_type=exam_type,
                user_message=user_message,
                user_role=user_role,
                evidence=evidence,
                language=language,
            )

    def _build_document_query(
        self,
        exam_type: str,
        document_category: str,
        document_text: str,
        user_message: str
    ) -> str:
        keywords = []
        lower_text = document_text.lower()
        if exam_type:
            keywords.append(exam_type)

        key_clinical_markers = [
            "nodule", "mass", "lesion", "consolidation", "effusion", "pneumothorax",
            "opacity", "edema", "hemorrhage", "infarct", "ischemia", "fracture",
            "steatosis", "cyst", "cholelithiasis", "appendicitis", "cardiomegaly",
            "elevated", "alt", "ast", "creatinine", "hemoglobin", "wbc", "platelets",
            "potassium", "glucose", "bilirubin", "gfr", "biopsy", "carcinoma", "dysplasia"
        ]
        for marker in key_clinical_markers:
            if marker in lower_text:
                keywords.append(marker)

        if user_message:
            keywords.append(user_message)

        query = " ".join(keywords[:10]) or exam_type or "medical imaging laboratory guidelines"
        return query[:2000]

    def _normalize_document_result(
        self,
        raw: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        document_category: str,
        exam_type: str
    ) -> Dict[str, Any]:
        raw_conditions = raw.get("possible_conditions") or []
        conditions = [
            self._normalize_condition(c)
            for c in raw_conditions
            if isinstance(c, dict) and c.get("name")
        ]

        warning_signs = [
            str(w).strip()
            for w in raw.get("warning_signs") or []
            if str(w).strip()
        ]

        urgency_level = self._normalize_urgency(raw.get("urgency_level"))
        urgency_level = self._enforce_urgency_floor(urgency_level, warning_signs)

        scan_findings = raw.get("scan_findings")
        if not isinstance(scan_findings, list):
            scan_findings = []

        abnormalities = [
            str(a).strip()
            for a in raw.get("abnormalities") or []
            if str(a).strip()
        ]

        trusted_solutions = raw.get("trusted_solutions")
        if not isinstance(trusted_solutions, list):
            trusted_solutions = []

        sources = self._evidence_sources(evidence)

        return {
            "reply": str(raw.get("reply") or raw.get("document_summary") or "").strip(),
            "document_category": raw.get("document_category") or document_category,
            "exam_type": raw.get("exam_type") or exam_type,
            "document_summary": str(raw.get("document_summary") or "").strip(),
            "scan_findings": scan_findings,
            "abnormalities": abnormalities,
            "possible_conditions": conditions,
            "warning_signs": warning_signs,
            "urgency_level": urgency_level,
            "trusted_solutions": trusted_solutions,
            "recommended_next_step": str(raw.get("recommended_next_step") or "").strip(),
            "sources": sources,
            "model_used": self.model or self.provider_name,
            "confidence": 0.9,
            "evidence": evidence,
        }

    def _mock_document_analysis(
        self,
        document_text: str,
        document_category: str,
        exam_type: str,
        user_message: str,
        user_role: str,
        evidence: List[Dict[str, Any]],
        language: str = "en",
    ) -> Dict[str, Any]:
        lower_text = document_text.lower()
        findings = []
        abnormalities = []
        warning_signs = []
        urgency = UrgencyLevel.ROUTINE_CONSULTATION

        if "nodule" in lower_text:
            findings.append({
                "area": "Lungs / Thorax",
                "finding": "Pulmonary nodule identified on chest imaging",
                "is_abnormal": True
            })
            abnormalities.append("Pulmonary nodule detected; risk stratification per Fleischner criteria warranted.")
            urgency = UrgencyLevel.PROMPT_MEDICAL_REVIEW
        if "effusion" in lower_text:
            findings.append({
                "area": "Pleural / Peritoneal space",
                "finding": "Fluid collection / effusion noted",
                "is_abnormal": True
            })
            abnormalities.append("Pleural or peritoneal fluid effusion identified.")
            urgency = UrgencyLevel.PROMPT_MEDICAL_REVIEW
        if "fracture" in lower_text:
            findings.append({
                "area": "Skeletal / Bone",
                "finding": "Bony cortical disruption / fracture identified",
                "is_abnormal": True
            })
            abnormalities.append("Bone fracture identified.")
            warning_signs.append("Acute bone fracture requiring orthopedic stabilization.")
            urgency = UrgencyLevel.URGENT_MEDICAL_ATTENTION
        if "hemorrhage" in lower_text or "bleed" in lower_text:
            findings.append({
                "area": "Neuro / Vascular",
                "finding": "Intracranial or acute hemorrhage indicated",
                "is_abnormal": True
            })
            abnormalities.append("Acute hemorrhage / bleeding identified.")
            warning_signs.append("Acute hemorrhage is a medical emergency requiring immediate emergency attention.")
            urgency = UrgencyLevel.URGENT_MEDICAL_ATTENTION
        if "steatosis" in lower_text or "fatty liver" in lower_text:
            findings.append({
                "area": "Liver / Hepatic",
                "finding": "Increased hepatic parenchymal echogenicity / steatosis",
                "is_abnormal": True
            })
            abnormalities.append("Hepatic steatosis (fatty liver changes).")
        if "cyst" in lower_text:
            findings.append({
                "area": "Kidney / Renal or Adnexal",
                "finding": "Well-circumscribed cystic lesion",
                "is_abnormal": False
            })
        if "alt" in lower_text or "ast" in lower_text:
            findings.append({
                "area": "Hepatic Function (Enzymes)",
                "finding": "Liver transaminase markers evaluated",
                "is_abnormal": "elevated" in lower_text or "high" in lower_text
            })
            if "elevated" in lower_text or "high" in lower_text:
                abnormalities.append("Elevated serum transaminases (ALT/AST).")
        if "hemoglobin" in lower_text or "cbc" in lower_text:
            findings.append({
                "area": "Hematology (CBC)",
                "finding": "Complete blood count and red cell parameters",
                "is_abnormal": "low" in lower_text or "anemia" in lower_text
            })
            if "low" in lower_text or "anemia" in lower_text:
                abnormalities.append("Decreased hemoglobin / hematocrit indicative of anemia.")

        if not findings:
            findings.append({
                "area": exam_type or "General Anatomy",
                "finding": "Clinical review of uploaded diagnostic document completed",
                "is_abnormal": False
            })
            urgency = UrgencyLevel.INFORMATIONAL

        possible_conditions = []
        if abnormalities:
            for abn in abnormalities[:3]:
                cond_name = abn.split(";")[0].replace("detected", "").replace("identified", "").strip()
                possible_conditions.append({
                    "name": cond_name.capitalize(),
                    "likelihood": "medium",
                    "confidence": "medium",
                    "description": f"Grounded in report findings: {abn}"
                })
        else:
            possible_conditions.append({
                "name": "Normal Diagnostic Study",
                "likelihood": "high",
                "confidence": "high",
                "description": "No acute focal abnormalities or alarming pathological indicators identified."
            })

        trusted_solutions = []
        if any("nodule" in f["finding"].lower() for f in findings):
            trusted_solutions.append({
                "action": "Repeat high-resolution chest CT scan in 6-12 months",
                "guideline_source": "Fleischner Society & ACR Imaging Guidelines",
                "details": "Follow-up imaging interval to monitor stability and assess doubling time."
            })
            trusted_solutions.append({
                "action": "Consultation with a Pulmonologist",
                "guideline_source": "NIH & WHO Clinical Protocols",
                "details": "Clinical correlation with smoking history, occupational exposures, and respiratory symptoms."
            })
        elif any("steatosis" in f["finding"].lower() for f in findings):
            trusted_solutions.append({
                "action": "Metabolic and lipid panel evaluation with lifestyle counseling",
                "guideline_source": "WHO & Mayo Clinic Guidelines",
                "details": "Evaluate fasting glucose, HbA1c, lipid panel, and dietary moderation."
            })
        elif any("fracture" in f["finding"].lower() or "hemorrhage" in f["finding"].lower() for f in findings):
            trusted_solutions.append({
                "action": "Immediate emergency evaluation and specialist consult",
                "guideline_source": "Emergency Medicine Clinical Practice Guidelines",
                "details": "Urgent intervention required to avoid acute complications."
            })
        else:
            trusted_solutions.append({
                "action": "Clinical correlation with your treating physician",
                "guideline_source": "WHO Clinical Decision Support Guidelines",
                "details": "Review the full scan and laboratory context alongside physical examination."
            })

        is_prof = str(user_role).upper() in {"DOCTOR", "PHARMACIST", "ADMIN"}
        sources = self._evidence_sources(evidence)
        study_title = exam_type or "Medical Diagnostic Study"

        if language == "rw":
            reply = (
                f"Isesengura ry'inyandiko y'ibipimo bya muganga: {study_title}.\n\n"
                f"Ibipimo byagaragaye: {len(findings)} byasuzumwe. "
                + (f"Ibipimo bikeneye kwitonderwa: {', '.join(abnormalities)}. " if abnormalities else "Nta kintu giteye inkeke cyabonetse. ")
                + "\nInama z'inzobere: Mwegere umuganga ubavura kugira ngo asuzume ibi bipimo mu buryo bwuzuye."
            )
            doc_summary = f"Isuzuma ry'ibipimo bya {study_title} ryakozwe hakurikijwe amabwiriza y'ubuvuzi yemewe."
            rec_step = "Kugisha inama umuganga ubishoboye kugira ngo agufashe gufata umwanzuro ukwiye."
        else:
            if is_prof:
                reply = (
                    f"**Clinical Document Analysis:** {study_title}\n\n"
                    f"**Findings Summary:** {len(findings)} anatomical regions/parameters evaluated. "
                    + (f"**Notable Observations:** {'; '.join(abnormalities)}. " if abnormalities else "No acute focal abnormalities identified. ")
                    + f"\n\n**Decision Support Guidance:** Grounded in retrieved evidence from {', '.join(s['name'] for s in sources[:3]) if sources else 'approved clinical guidelines'}. "
                    "Review recommended next steps and correlate with patient clinical history."
                )
            else:
                reply = (
                    f"Here is a clear analysis of your uploaded **{study_title}** results:\n\n"
                    + (f"**What the report found:** We identified {len(findings)} key observations. "
                       f"The main items noted are: {'; '.join(abnormalities)}.\n\n" if abnormalities
                       else "**What the report found:** The diagnostic findings appear generally unremarkable with no critical alerts.\n\n")
                    + f"**Recommended Next Step:** {trusted_solutions[0]['action']}. "
                    "Please bring this report to your healthcare provider for clinical correlation and personalized advice."
                )
            doc_summary = f"Clinical review of {study_title} findings and laboratory indicators grounded in trusted medical evidence."
            rec_step = trusted_solutions[0]["action"]

        return {
            "reply": reply,
            "document_category": document_category,
            "exam_type": study_title,
            "document_summary": doc_summary,
            "scan_findings": findings,
            "abnormalities": abnormalities,
            "possible_conditions": possible_conditions,
            "warning_signs": warning_signs,
            "urgency_level": urgency,
            "trusted_solutions": trusted_solutions,
            "recommended_next_step": rec_step,
            "sources": sources,
            "model_used": "mock",
            "confidence": 0.85,
            "evidence": evidence,
        }

    def generate_follow_up_questions(
        self,
        consultation_context: Dict,
        current_symptoms: List[str]
    ) -> List[str]:
        """
        Generate follow-up questions based on current information.

        Args:
            consultation_context: Current consultation information
            current_symptoms: Symptoms already identified

        Returns:
            List of follow-up questions
        """
        # The chief complaint, the clinician's notes and the symptoms already on
        # the consultation carry the context an empty current_symptoms list would
        # otherwise lose, which made every caller get the same two questions.
        context = consultation_context or {}
        context_text = " ".join(
            str(value)
            for value in (context.get("chief_complaint"), context.get("notes"))
            if value
        )

        symptoms = [str(s) for s in (current_symptoms or []) if s]
        for symptom in list(context.get("symptoms") or []) + self._extract_symptoms_from_text(
            f"{context_text} {' '.join(symptoms)}"
        ):
            if str(symptom).lower() not in {s.lower() for s in symptoms}:
                symptoms.append(str(symptom))

        language = self._detect_language(context_text or " ".join(symptoms), [])
        already_asked = set(context.get("already_asked") or [])
        questions = [
            question
            for question in (
                self._mock_follow_up_questions(symptoms, language)
                + self._mock_secondary_questions(symptoms, language)
            )
            if question not in already_asked
        ]
        return questions[:3]

    def _use_llm_provider(self) -> bool:
        if self.provider_name == "mock":
            return False
        if not self.api_key:
            logger.warning(
                "AI provider %r configured without AI_API_KEY; using fallback conversation.",
                self.provider_name,
            )
            return False
        return True

    def _retrieve_evidence(self, query: str) -> List[Dict[str, Any]]:
        try:
            return self.retrieval_service.retrieve_evidence(
                query=query, max_results=self.MAX_EVIDENCE_RESULTS
            )
        except Exception as exc:  # retrieval must never break the conversation
            logger.warning("Evidence retrieval failed: %s", exc)
            return []

    def _build_query(self, history: List[Dict[str, str]], message: str) -> str:
        user_turns = [turn["content"] for turn in history if turn["role"] == "user"]
        query = " ".join(user_turns[-3:] + [message])
        recognized_symptoms = self._extract_symptoms_from_text(query)
        if recognized_symptoms:
            query = f"{query} {' '.join(recognized_symptoms)}"
        return query[:2000]

    def _sanitize_history(
        self, history: Optional[List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        sanitized = []
        for turn in history or []:
            if not isinstance(turn, dict):
                continue
            role = turn.get("role")
            content = (turn.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                sanitized.append({"role": role, "content": content[:2000]})
        return sanitized[-self.MAX_HISTORY_MESSAGES:]

    def _build_messages(
        self,
        message: str,
        history: List[Dict[str, str]],
        patient_history: Optional[Dict],
        current_medications: Optional[List[str]],
        evidence: List[Dict[str, Any]],
        language: str = "en",
    ) -> List[Dict[str, str]]:
        patient_context = {}
        if patient_history:
            patient_context["medical_history"] = patient_history
        if current_medications:
            patient_context["current_medications"] = current_medications

        system_prompt = get_chat_system_prompt(
            evidence_block=self.retrieval_service.format_evidence_for_ai(evidence),
            patient_context=patient_context or None,
            language=language,
        )
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})
        return messages

    def _build_professional_messages(
        self,
        message: str,
        history: List[Dict[str, str]],
        professional_context: Optional[Dict],
        evidence: List[Dict[str, Any]],
        language: str = "en",
    ) -> List[Dict[str, str]]:
        system_prompt = get_professional_system_prompt(
            evidence_block=self.retrieval_service.format_evidence_for_ai(evidence),
            professional_context=professional_context or None,
            language=language,
        )
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})
        return messages

    @staticmethod
    def _plain_text(value: Any) -> str:
        """Make the model's text safe for a plain-text renderer and for speech.

        Measured live: the reasoning model sometimes double-escapes line breaks, so
        the parsed JSON string contains a literal backslash-n. In a
        ``white-space: pre-wrap`` block that shows up as visible "\n" noise and a
        text-to-speech reader says it out loud, so it is normalised here. Real
        newlines parse without a backslash and are untouched.
        """
        text = str(value or "")
        if "\\n" in text:
            text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
        return text.strip()

    def _normalize_result(
        self, raw: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        urgency_level = self._normalize_urgency(raw.get("urgency_level"))
        warning_signs = [
            self._plain_text(w) for w in raw.get("warning_signs") or [] if self._plain_text(w)
        ][:10]
        urgency_level = self._enforce_urgency_floor(urgency_level, warning_signs)

        general_information = self._plain_text(raw.get("general_information"))
        recommended_next_step = self._plain_text(
            raw.get("recommended_next_step") or self._generate_recommendation(urgency_level)
        )
        reply = self._plain_text(raw.get("reply"))
        if not reply:
            reply = " ".join(part for part in (general_information, recommended_next_step) if part)

        return {
            "reply": reply,
            "symptoms_identified": [str(s) for s in raw.get("symptoms_identified") or []][:10],
            "follow_up_questions": [str(q) for q in raw.get("follow_up_questions") or []][:3],
            "possible_conditions": [
                self._normalize_condition(condition)
                for condition in raw.get("possible_conditions") or []
                if isinstance(condition, dict)
            ][:5],
            "warning_signs": warning_signs,
            "urgency_level": urgency_level,
            "general_information": general_information,
            "medication_information": raw.get("medication_information") or [],
            "recommended_next_step": recommended_next_step,
            # Citations always come from the actual retrieval, never from the LLM.
            "sources": self._evidence_sources(evidence),
            "model_used": self.model,
            "confidence": self._normalize_confidence(raw.get("confidence")),
            "evidence": evidence,
        }

    def _mock_conversation(
        self,
        message: str,
        history: List[Dict[str, str]],
        patient_history: Optional[Dict],
        current_medications: Optional[List[str]],
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Deterministic conversational reply used without an LLM provider."""
        patient_text = " ".join(
            [turn["content"] for turn in history if turn["role"] == "user"] + [message]
        )
        previously_asked = [
            turn["content"] for turn in history if turn["role"] == "assistant"
        ]
        language = self._detect_language(message, history)

        current_symptoms = self._extract_symptoms_from_text(message)
        symptoms = current_symptoms or self._extract_symptoms_from_text(patient_text)
        follow_up_questions = [
            question
            for question in (
                self._mock_follow_up_questions(symptoms, language)
                + self._mock_secondary_questions(symptoms, language)
            )
            if not any(question in text for text in previously_asked)
        ][:3]
        urgency_level = self._determine_urgency(patient_text, symptoms)
        warning_signs = self._check_warning_signs(patient_text, symptoms)
        urgency_level = self._enforce_urgency_floor(urgency_level, warning_signs)
        general_information = self._generate_general_information(symptoms, language)

        lines = []
        if warning_signs:
            if language == "rw":
                lines.append(
                    "Ibimenyetso by'akaga byavuzwe bisaba isuzuma ryihuse ry'ubuvuzi: "
                    + ", ".join(warning_signs)
                    + "."
                )
            else:
                lines.append(
                    "Warning signs you mentioned need prompt medical review: "
                    + ", ".join(warning_signs)
                    + "."
                )
        if symptoms:
            if language == "rw":
                lines.append("Murakoze — nabonye ibimenyetso mwambwiye: " + ", ".join(symptoms) + ".")
            else:
                lines.append("Thanks — I've noted: " + ", ".join(symptoms) + ".")
        else:
            if language == "rw":
                lines.append("Murakoze kudusangiza aya makuru.")
            else:
                lines.append("Thanks for sharing that.")

        evidence_lines = []
        for index, item in enumerate(evidence[:3], 1):
            snippet = (item.get("content") or "").strip().split(".")[0][:180]
            evidence_lines.append(
                f"[{index}] {item.get('title')} — {item.get('source_name')}: {snippet}."
            )
        if evidence_lines:
            if language == "rw":
                lines.append("Amakuru yakuwe mu nkomoko z'ubuvuzi zemewe:\n" + "\n".join(evidence_lines))
            else:
                lines.append("From trusted sources:\n" + "\n".join(evidence_lines))
        else:
            if language == "rw":
                lines.append(
                    "Ntabwo nabonye amabwiriza ahagije mu nkomoko zemewe z'ubuvuzi. "
                    "Ni ngombwa kugisha inama umuganga cyangwa inzobere mu buvuzi."
                )
            else:
                lines.append(
                    "I couldn't find guidance on this in the approved medical sources yet; "
                    "a healthcare professional can help with this directly."
                )

        if general_information:
            lines.append(general_information)
        if follow_up_questions:
            prefix = "Kugira ngo mbashe kumva neza amakuru y'ubuzima bwanyu:\n" if language == "rw" else "To help me understand better:\n"
            lines.append(
                prefix + "\n".join(
                    f"{index}. {question}"
                    for index, question in enumerate(follow_up_questions, 1)
                )
            )
        recommendation = self._generate_recommendation(urgency_level, language)
        lines.append(recommendation)

        return {
            "reply": "\n\n".join(lines),
            "symptoms_identified": symptoms,
            "follow_up_questions": follow_up_questions,
            "possible_conditions": self._mock_possible_conditions(symptoms, language),
            "warning_signs": warning_signs,
            "urgency_level": urgency_level,
            "general_information": general_information,
            "medication_information": [],
            "recommended_next_step": recommendation,
            "sources": self._evidence_sources(evidence),
            "model_used": "mock",
            "confidence": 0.5,
            "evidence": evidence,
        }

    def _mock_professional_conversation(
        self,
        message: str,
        history: List[Dict[str, str]],
        evidence: List[Dict[str, Any]],
        fallback_reason: str = "",
    ) -> Dict[str, Any]:
        """Deterministic clinician-facing reply used without an LLM provider.

        ``fallback_reason`` is set when a configured provider was tried and failed,
        so the note tells the clinician the real cause instead of blaming a missing
        API key.
        """
        query = " ".join(
            [turn["content"] for turn in history if turn["role"] == "user"] + [message]
        )
        language = self._detect_language(message, history)

        evidence_lines = []
        for index, item in enumerate(evidence[:4], 1):
            snippet = (item.get("content") or "").strip().split(".")[0][:220]
            evidence_lines.append(
                f"[{index}] {item.get('title')} — {item.get('source_name')}: {snippet}."
            )

        rw = language == "rw"
        lines = []
        if evidence_lines:
            lines.append(
                ("Incamake y'amabwiriza yakuwe mu nkomoko z'ubuvuzi zemewe:\n"
                 if rw
                 else "From the approved medical sources for your query:\n")
                + "\n".join(evidence_lines)
            )
        else:
            lines.append(
                "Ntabwo nabonye inyandiko ihuye n'ikibazo mwabajije mu nkomoko zemewe."
                if rw
                else "No matching guidance was found in the approved medical sources for this query."
            )

        if fallback_reason:
            # A configured provider was tried and failed (truncated reply, quota,
            # outage). Say so instead of blaming an unset API key.
            short_reason = fallback_reason[:200]
            lines.append(
                "Icyitonderwa: Igisubizo cya AI nticyakoresijwe kubera ikibazo cya "
                "serivisi y'ikoranabuhanga, si ikibazo cy'uwo gutanga API key. Ibi "
                "bikurikira bivuye mu nkomoko zemewe gusa."
                if rw
                else "Note: the model answer could not be used ("
                + short_reason
                + "), so this reply is limited to retrieved source excerpts. "
                "This is a provider/runtime issue, not a missing API key."
            )
        elif rw:
            lines.append(
                "Icyitonderwa: Nta funguro rya AI (AI_API_KEY) ryashyizweho. Ibisubizo bivuye "
                "mu nkomoko zemewe gusa. Shyiraho AI_PROVIDER na AI_API_KEY mu kubona isuzuma ryuzuye."
            )
        else:
            lines.append(
                "Note: no LLM provider is configured (AI_API_KEY is empty), so this reply "
                "is limited to retrieved source excerpts. Configure AI_PROVIDER and "
                "AI_API_KEY for full conversational answers."
            )

        recommendation = (
            "Koresha amakuru yakuwe mu nkomoko zemewe nk'ubufasha; "
            "icyemezo cya kliniki kiguma kuri mwe."
            if rw
            else "Treat the excerpts above as the retrieved evidence; the clinical "
            "judgment remains yours."
        )

        return {
            "reply": "\n\n".join(lines),
            "symptoms_identified": self._extract_symptoms_from_text(query),
            "follow_up_questions": [],
            "possible_conditions": [],
            "warning_signs": self._check_warning_signs(query, []),
            "urgency_level": self._determine_urgency(query, []),
            "general_information": "\n".join(evidence_lines),
            "medication_information": [],
            "recommended_next_step": recommendation,
            "sources": self._evidence_sources(evidence),
            "model_used": "mock",
            "confidence": 0.4,
            "evidence": evidence,
        }

    def _evidence_sources(self, evidence: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        sources = []
        seen = set()
        for item in evidence:
            key = item.get("url") or item.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            sources.append({
                "name": item.get("source_name") or "Unknown",
                "title": item.get("title") or "",
                "url": item.get("url") or "",
            })
        return sources

    def _normalize_urgency(self, value: Any) -> str:
        urgency = str(value or "").upper()
        if urgency in dict(UrgencyLevel.CHOICES):
            return urgency
        return UrgencyLevel.ROUTINE_CONSULTATION

    def _enforce_urgency_floor(self, urgency_level: str, warning_signs: List[str]) -> str:
        if warning_signs and urgency_level in (
            UrgencyLevel.INFORMATIONAL,
            UrgencyLevel.ROUTINE_CONSULTATION,
        ):
            return UrgencyLevel.PROMPT_MEDICAL_REVIEW
        return urgency_level

    def _normalize_condition(self, condition: Dict[str, Any]) -> Dict[str, str]:
        likelihood = str(condition.get("likelihood") or "low").lower()
        if likelihood not in _VALID_LIKELIHOODS:
            likelihood = "low"
        return {
            "name": str(condition.get("name") or ""),
            "likelihood": likelihood,
            "confidence": likelihood,
            "description": str(condition.get("description") or ""),
        }

    def _normalize_confidence(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.5

    def _detect_language(self, text: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Return the conversation language using exact token matching and history."""
        lowered = (text or "").lower()
        words = [w.strip("?,.!;:\"'()") for w in lowered.split()]
        
        # 1. Exact word match against Kinyarwanda vocabulary
        if any(word in _KINYARWANDA_KEYWORDS for word in words):
            return "rw"
            
        # 2. Check individual words against question particles and agglutinative prefixes
        kinyarwanda_particles = {
            "iki", "ngo", "nte", "nza", "nki", "ryari", "gute", "he", "se", "yego", "oya",
            "kuri", "muri", "mbigenze", "nakoresha", "nakora", "bigabanuke", "kuba", "bita",
            "hafi", "mu", "ku", "cya", "bya", "za", "wa", "ya", "ra", "wanjye", "yawe",
            "yacu", "yanyu", "wacu", "wanyu", "cyanjye", "byanjye", "ufite", "bafite"
        }
        for word in words:
            if word in kinyarwanda_particles:
                return "rw"
            if len(word) >= 4 and word.startswith((
                "nd", "rw", "nsh", "bw", "cy", "ny", "kw", "gw", "tuk", "mub",
                "nak", "bik", "big", "bim", "bir", "bak", "bag", "bam", "bar",
                "tug", "tuk", "tur", "kug", "kur", "gug", "gur", "ura", "ira", "bira"
            )) and not self._is_english_word(word):
                return "rw"

        if any(ch in lowered for ch in ("é", "è", "ô", "î", "à", "ù", "ê")):
            return "rw"

        # 3. Check recent history if current message is ambiguous
        if history:
            for turn in reversed(history):
                if isinstance(turn, dict) and turn.get("role") == "user":
                    turn_words = [w.strip("?,.!;:\"'()") for w in (turn.get("content") or "").lower().split()]
                    if any(word in _KINYARWANDA_KEYWORDS for word in turn_words):
                        return "rw"

        return "en"

    @staticmethod
    def _is_english_word(word: str) -> bool:
        """Filter out common English words to prevent false prefix matches."""
        english_words = {
            "the", "and", "for", "you", "can", "what", "how", "have", "with", "from",
            "that", "this", "will", "should", "would", "does", "are", "were", "was",
            "been", "or", "not", "yes", "in", "on", "at", "to", "by", "my", "your",
            "his", "her", "our", "their", "it", "its", "turn", "take", "make", "cure",
            "care", "burn", "back", "sick", "pain", "head", "cough", "drug", "doctor",
            "hello", "hi", "hey", "good", "morning", "afternoon", "evening", "risk",
            "interaction", "metronidazole", "warfarin", "clinical", "assistant"
        }
        return word.lower() in english_words

    def _is_general_greeting(self, text: str) -> bool:
        normalized = " ".join(
            (text or "").lower().replace("!", "").replace(",", "").split()
        )
        return normalized in {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "muraho",
            "muraho neza",
            "mwaramutse",
            "mwaramutse neza",
            "mwiriwe",
            "mwiriwe neza",
        }

    def _is_incomplete_message(self, text: str) -> bool:
        """Avoid medical conclusions when the latest message is not actionable."""
        normalized = " ".join((text or "").split())
        return len(normalized) < 3

    def _clarification_result(self, language: str) -> Dict[str, Any]:
        if language == "rw":
            reply = (
                "Ntabwo nasobanukiwe neza ubutumwa bwanyu. Nyamuneka sobanura ikibazo "
                "cy'ubuzima cyangwa ibimenyetso mufite, igihe byatangiriye, n'uko bikomeye."
            )
            next_step = "Sobanura ikibazo cyangwa ibimenyetso byanyu mbere yo gusuzumwa."
        else:
            reply = (
                "I’m not sure what you mean yet. Please describe your health question "
                "or symptoms, when they started, and how severe they are."
            )
            next_step = "Provide more detail about the health concern before assessment."

        return {
            "reply": reply,
            "symptoms_identified": [],
            "follow_up_questions": [
                "What symptoms or health question would you like help with?"
                if language == "en" else "Ni ibihe bimenyetso cyangwa ikibazo cy'ubuzima mwifuza ko tubafashamo?"
            ],
            "possible_conditions": [],
            "warning_signs": [],
            "urgency_level": UrgencyLevel.INFORMATIONAL,
            "general_information": "",
            "medication_information": [],
            "recommended_next_step": next_step,
            "sources": [],
            "model_used": "conversation_router",
            "confidence": 1.0,
            "evidence": [],
        }

    def _greeting_result(self, language: str, professional: bool = False) -> Dict[str, Any]:
        if professional:
            if language == "rw":
                reply = (
                    "Muraho! Ndi umufasha mu gufata ibyemezo by'ubuvuzi. Mumbaze ku ndwara "
                    "zishoboka, umutekano w'imiti, imivangwa y'imiti, cyangwa amabwiriza yemewe."
                )
            else:
                reply = (
                    "Hello! I'm your clinical decision support assistant. Ask me about "
                    "differentials, medications, interactions, or the approved guidance "
                    "for a case you're reviewing."
                )
        elif language == "rw":
            reply = "Muraho! Nabafasha nte uyu munsi? Mwashobora kumbwira ibimenyetso cyangwa ikibazo cy'ubuzima mufite."
        else:
            reply = "Hello! How can I help you? You can tell me about any symptoms or health question you have."

        return {
            "reply": reply,
            "symptoms_identified": [],
            "follow_up_questions": [],
            "possible_conditions": [],
            "warning_signs": [],
            "urgency_level": UrgencyLevel.INFORMATIONAL,
            "general_information": "",
            "medication_information": [],
            "recommended_next_step": "",
            "sources": [],
            "model_used": "conversation_router",
            "confidence": 1.0,
            "evidence": [],
        }

    def _extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract symptoms from natural language text (supports English and Kinyarwanda)."""
        symptom_keywords = {
            "fever": ["fever", "umuriro", "ubushyuhe", "furere"],
            "headache": ["headache", "umutwe", "umutwe urampandura", "umutwe urandya"],
            "cough": ["cough", "kosora", "inkorora", "guhumeka", "guhumeka nabi"],
            "body pain": ["body pain", "ububabare bwo mu mubiri", "umubiri urambabaza", "kuribwa mu ngingo"],
            "stomach pain": [
                "stomach pain",
                "ububabare mu nda",
                "urababara mu nda",
                "ndababara mu nda",
                "mbabara mu nda",
                "nda irambabaza",
                "igifu",
            ],
            "nausea": ["nausea", "isazi", "ikimunyu", "gusesema", "isesemi"],
            "vomiting": ["vomiting", "kuhira", "kuruka"],
            "diarrhea": ["diarrhea", "diarrhoea", "dysenterie", "turasuka", "impiswi", "gucibwamo"],
            "fatigue": ["fatigue", "umunaniro", "kunanirwa", "naniwe", "naniwe cyane", "gucika intege"],
            "dizziness": ["dizziness", "ikizunguzungu", "ibibendo", "kuzungerwa"],
            "chest pain": ["chest pain", "ububabare mu gituza", "mugituza", "igituza"],
            "shortness of breath": ["shortness of breath", "kubura umwuka", "guhumeka bigoranye"],
            "sore throat": ["sore throat", "umunwa urabubabaza", "umutwe wo mu muhogo", "muhogo"],
            "runny nose": ["runny nose", "imibiri itemba", "amazuru asohora", "ibicurane"],
            "rash": ["rash", "uburuka", "indwara y'uruhu", "ibiheri"],
            "chills": ["chills", "ubukonje", "gutakaza ubushyuhe", "gutitira"],
            "joint pain": ["joint pain", "ububabare mu ngingo"],
            "back pain": [
                "back pain",
                "pain in my back",
                "ububabare bwo mu mugongo",
                "umugongo urambabaza",
                "mbabara umugongo",
                "mbabara mu mugongo",
                "ndumva mbabara umugongo",
                "umugongo",
            ],
        }

        text_lower = text.lower()
        found_symptoms = []
        for display_name, keyword_variants in symptom_keywords.items():
            if any(keyword in text_lower for keyword in keyword_variants):
                if "umuriro" in text_lower and display_name == "fever":
                    found_symptoms.append("Umuriro")
                elif "umutwe" in text_lower and display_name == "headache":
                    found_symptoms.append("Umutwe urampandura")
                elif ("nda" in text_lower or "igifu" in text_lower) and display_name == "stomach pain":
                    found_symptoms.append("Ububabare bwo mu nda")
                elif "naniwe" in text_lower and display_name == "fatigue":
                    found_symptoms.append("Umunaniro ukabije")
                else:
                    found_symptoms.append(display_name.capitalize())

        return found_symptoms

    def _mock_follow_up_questions(self, symptoms: List[str], language: str = "en") -> List[str]:
        """Generate mock follow-up questions based on symptoms."""
        lower_symptoms = [s.lower() for s in symptoms]
        questions = []

        if "fever" in lower_symptoms or "umuriro" in lower_symptoms:
            if language == "rw":
                questions.append("Umuriro mufite watangiye ryari, kandi uri ku he ngero?")
                questions.append("Mwaba mwafashe umuti ugabanya umuriro nka paracetamol?")
            else:
                questions.append("How high is your fever and when did it start?")
                questions.append("Have you taken any medication for the fever?")

        if "headache" in lower_symptoms or "umutwe" in lower_symptoms:
            if language == "rw":
                questions.append("Ububabare bw'umutwe buri ku he gice neza?")
                questions.append("Mwabuvuga ute (burashikira, burashushuza, cyangwa buragukomera)?")
            else:
                questions.append("Where exactly is the headache located?")
                questions.append("How would you describe the pain (sharp, dull, throbbing)?")

        if "cough" in lower_symptoms:
            if language == "rw":
                questions.append("Inkorora mufite irumye cyangwa ikora ibitose?")
                questions.append("Ibyo bimenyetso bimaze igihe kingana gute?")
            else:
                questions.append("Is the cough dry or do you produce phlegm?")
                questions.append("How long have you had the cough?")

        if "back pain" in lower_symptoms:
            if language == "rw":
                questions.append("Ububabare bwo mu mugongo bumaze igihe kingana gute?")
                questions.append("Mwaba mwarakomeretse, waguye, cyangwa mwarazamuye ikintu kiremereye?")
                questions.append("Hari ukunanirwa mu maguru cyangwa ikibazo cyo gufata inkari?")
            else:
                questions.append("How long have you had the back pain?")
                questions.append("Were you injured, did you fall, or lift something heavy?")
                questions.append("Do you have leg weakness or numbness, or trouble controlling your bladder?")

        if "stomach pain" in lower_symptoms:
            if language == "rw":
                questions.append("Ububabare bwo mu nda bumaze igihe kingana gute, kandi buri ku he gice neza?")
                questions.append("Mwaba mufite kuruka, impiswi, umuriro, cyangwa amaraso mu musarane?")
                questions.append("Ububabare burakomeye cyangwa buragenda bwiyongera?")
            else:
                questions.append("How long have you had the abdominal pain, and where exactly is it?")
                questions.append("Do you have vomiting, diarrhea, fever, or blood in vomit or stool?")
                questions.append("Is the pain severe or getting worse?")

        if "fatigue" in lower_symptoms or "umunaniro" in lower_symptoms:
            if language == "rw":
                questions.append("Umunaniro ukabije watangiye ryari, kandi kuruhuka birawugabanya?")
                questions.append("Mwaba mufite umuriro, kubura umwuka, kuzungerwa, cyangwa kugwa igihumure?")
                questions.append("Mwaba mufite izindi indwara karande cyangwa imiti mwatangiye gufata vuba?")
            else:
                questions.append("When did the severe tiredness start, and does rest improve it?")
                questions.append("Do you have fever, shortness of breath, dizziness, or fainting?")
                questions.append("Do you have other medical conditions or recently started any medicines?")

        if not questions:
            if language == "rw":
                questions.append("Ibyo bimenyetso bimaze igihe kingana gute?")
                questions.append("Mwaba mwarabonye izindi mpinduka mu buzima bwanyu?")
            else:
                questions.append("How long have you been experiencing these symptoms?")
                questions.append("Have you noticed any other changes in your health?")

        return questions[:3]

    def _mock_secondary_questions(self, symptoms: List[str], language: str = "en") -> List[str]:
        """Deeper questions asked once the first round has been answered."""
        lower_symptoms = [s.lower() for s in symptoms]
        questions = []

        if "fever" in lower_symptoms or "umuriro" in lower_symptoms:
            if language == "rw":
                questions.append("Hari gutitira, gushyuha cyane, cyangwa ko mu ijosi hakomerera?")
                questions.append("Waba warakorewe isuzuma rya malaria?")
            else:
                questions.append("Does the fever come with chills, sweating, or a stiff neck?")
                questions.append("Have you been tested for malaria?")
        if "headache" in lower_symptoms or "umutwe" in lower_symptoms:
            if language == "rw":
                questions.append("Urumuri cyangwa urusaku birongera ububabare?")
            else:
                questions.append("Does light or sound make the headache worse?")
        if "cough" in lower_symptoms:
            if language == "rw":
                questions.append("Hari ububabare mu gituza cyangwa guhumeka bigoranye?")
            else:
                questions.append("Does the cough come with chest pain or difficulty breathing?")
        if "diarrhea" in lower_symptoms:
            if language == "rw":
                questions.append("Urashobora kunywa amazi ahagije, kandi uyaherukamo kangahe ku munsi?")
            else:
                questions.append("Are you able to keep fluids down, and how many times a day is the diarrhea?")
        if "rash" in lower_symptoms:
            if language == "rw":
                questions.append("Ibiheri byatangiye he, kandi biragenda bikwira?")
            else:
                questions.append("Where did the rash start, and is it spreading?")
        if "shortness of breath" in lower_symptoms or "difficulty breathing" in lower_symptoms or "guhumeka bigoranye" in lower_symptoms:
            if language == "rw":
                questions.append("Guhumeka bigoranye byiyongera iyo uryamye cyangwa ukora ibikorwa?")
            else:
                questions.append("Does the breathing difficulty get worse when you lie down or with activity?")

        if language == "rw":
            questions.append("Hari ikintu kigabanya cyangwa cyongera ibimenyetso?")
            questions.append("Ufite izindi ndwara karande cyangwa imiti uri gufata?")
        else:
            questions.append("Is there anything that makes your symptoms better or worse?")
            questions.append("Do you have any long-term conditions or are you taking any medicines?")
        return questions

    def _determine_urgency(self, patient_input: str, symptoms: List[str]) -> str:
        """Determine urgency level based on symptoms."""
        emergency_keywords = [
            "chest pain", "difficulty breathing", "severe bleeding", "loss of consciousness",
            "ukunanirwa mu maguru", "gufata inkari", "umwanda utabasha kuwufata",
            "ububabare mu gituza", "kubura umwuka"
        ]
        text_lower = patient_input.lower()

        for keyword in emergency_keywords:
            if keyword in text_lower:
                return UrgencyLevel.URGENT_MEDICAL_ATTENTION

        severe_symptoms = ["high fever", "severe pain", "vomiting blood", "umuriro ukabije", "kuruka amaraso"]
        for symptom in severe_symptoms:
            if symptom in text_lower:
                return UrgencyLevel.PROMPT_MEDICAL_REVIEW

        return UrgencyLevel.ROUTINE_CONSULTATION

    def _mock_possible_conditions(self, symptoms: List[str], language: str = "en") -> List[Dict]:
        """Generate mock possible conditions based on symptoms."""
        lower_symptoms = [s.lower() for s in symptoms]
        conditions = []

        if "fever" in lower_symptoms or "umuriro" in lower_symptoms:
            if language == "rw":
                conditions.append({
                    "name": "Indwara y'ubwandu bwa virusi cyangwa agakoko",
                    "likelihood": "medium",
                    "description": "Indwara z'ubwandu bwa virusi zishobora gutera umuriro no gutitira.",
                })
            else:
                conditions.append({
                    "name": "Viral infection",
                    "likelihood": "medium",
                    "description": "Common viral infections include flu and common cold",
                })

        if "headache" in lower_symptoms or "umutwe" in lower_symptoms:
            if language == "rw":
                conditions.append({
                    "name": "Umutwe wo gushikira no kunanirwa",
                    "likelihood": "medium",
                    "description": "Umutwe ushobora guturuka ku kunanirwa, umuhangayiko, cyangwa kuryama nabi.",
                })
            else:
                conditions.append({
                    "name": "Tension headache",
                    "likelihood": "medium",
                    "description": "Most common type of headache, often caused by stress",
                })

        if "cough" in lower_symptoms:
            if language == "rw":
                conditions.append({
                    "name": "Indwara y'ubuhumekero yo hejuru",
                    "likelihood": "medium",
                    "description": "Ubwandu bwo mu muhamagaro na mu muhogo bukunze gutera inkorora.",
                })
            else:
                conditions.append({
                    "name": "Upper respiratory infection",
                    "likelihood": "medium",
                    "description": "Infection of the nose, throat, or sinuses",
                })

        return conditions

    def _check_warning_signs(self, patient_input: str, symptoms: List[str]) -> List[str]:
        """Check for emergency warning signs."""
        warning_signs = []
        emergency_indicators = [
            "chest pain", "shortness of breath", "difficulty breathing",
            "severe pain", "sudden weakness", "slurred speech",
            "loss of consciousness", "confusion",
            "ukunanirwa mu maguru", "gufata inkari", "umwanda utabasha kuwufata",
            "ububabare mu gituza", "kubura umwuka"
        ]

        text_lower = patient_input.lower()
        for indicator in emergency_indicators:
            if indicator in text_lower:
                warning_signs.append(indicator.replace("_", " ").capitalize())

        return warning_signs

    def _generate_general_information(self, symptoms: List[str], language: str = "en") -> str:
        """Generate general medical information."""
        if not symptoms:
            if language == "rw":
                return "Nyamuneka sangiza amakuru arambuye ku bimenyetso byanyu kugira ngo dusuzume neza."
            return "Please provide more details about your symptoms for better assessment."

        symptom_list = ", ".join(symptoms)
        if language == "rw":
            return (
                f"Hashingiwe ku bimenyetso mwambwiye ({symptom_list}), bishobora kuba bifitanye isano n'indwara zinyuranye. "
                "Ni ngombwa gukomeza kureba uko ibimenyetso bimereye no kugisha inama inzobere mu buvuzi."
            )
        return f"Based on the symptoms you've described ({symptom_list}), this could be related to several conditions. It's important to monitor your symptoms and seek professional medical advice if they persist or worsen."

    def _generate_recommendation(self, urgency_level: str, language: str = "en") -> str:
        """Generate appropriate recommendation based on urgency."""
        recommendations = {
            "INFORMATIONAL": {
                "en": "Monitor your symptoms and maintain good hydration. Consult a healthcare provider if symptoms persist.",
                "rw": "Komeza gukurikirana ibimenyetso byanyu no kunywa amazi ahagije. Gana ivuriro niba ibimenyetso bikomeje.",
            },
            "ROUTINE_CONSULTATION": {
                "en": "Schedule an appointment with your healthcare provider within the next few days for proper evaluation.",
                "rw": "Shaka gahunda yo kurebwa n'umuganga mu minsi mike iri imbere kugira ngo musuzumwe neza.",
            },
            "PROMPT_MEDICAL_REVIEW": {
                "en": "Seek medical attention within 24 hours for proper evaluation and treatment.",
                "rw": "Gana ivuriro mu masaha 24 ari imbere kugira ngo musuzumwe kandi muhabwe ubuvuzi bukwiriye.",
            },
            "URGENT_MEDICAL_ATTENTION": {
                "en": "Seek immediate medical attention. Call emergency services or go to the nearest emergency room.",
                "rw": "Shaka ubuvuzi bwihutirwa vuba na vuba. Hamagara serivisi z'ubutabazi cyangwa mugane ibitaro bibegereye.",
            },
        }

        return recommendations.get(urgency_level, recommendations["ROUTINE_CONSULTATION"])[language]
