"""Evaluation engine for Kinyarwanda and multilingual clinical AI systems.

Evaluates 5 core dimensions:
1. Correctness (clinical triage, factual medical accuracy, absence of hallucinations)
2. Kinyarwanda Grammar (respectful honorific register, noun-class concords, spelling)
3. Naturalness (authentic Rwandan phrasing, absence of awkward word-for-word translation calques)
4. Understanding of User Intentions (comprehension of code-switching, language preference adherence)
5. Relevance (direct grounding, avoidance of irrelevant filler, contextual follow-ups)
"""

from dataclasses import dataclass, field
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.glossary import requests_kinyarwanda, requests_english


@dataclass
class DimensionScore:
    """Score for a specific evaluation dimension."""
    dimension: str
    score: float  # 0.0 to 100.0
    weight: float
    passed: bool
    feedback: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Complete evaluation result for a single question prompt."""
    prompt_id: str
    category: str
    prompt: str
    expected_language: str
    detected_language: str
    response_text: str
    correctness: DimensionScore
    grammar: DimensionScore
    naturalness: DimensionScore
    intent_understanding: DimensionScore
    relevance: DimensionScore
    overall_score: float
    passed: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "category": self.category,
            "prompt": self.prompt,
            "expected_language": self.expected_language,
            "detected_language": self.detected_language,
            "overall_score": round(self.overall_score, 2),
            "passed": self.passed,
            "scores": {
                "correctness": round(self.correctness.score, 2),
                "grammar": round(self.grammar.score, 2),
                "naturalness": round(self.naturalness.score, 2),
                "intent_understanding": round(self.intent_understanding.score, 2),
                "relevance": round(self.relevance.score, 2),
            },
            "feedback": {
                "correctness": self.correctness.feedback,
                "grammar": self.grammar.feedback,
                "naturalness": self.naturalness.feedback,
                "intent": self.intent_understanding.feedback,
                "relevance": self.relevance.feedback,
            }
        }


# Linguistic markers for Kinyarwanda evaluation
POLITE_HONORIFIC_MARKERS = [
    "mwaba", "mufite", "bwanyu", "mwisuzumishe", "mugane", "mwebwe",
    "mwashobora", "mubwire", "muramutse", "mushobora", "mwakora",
    "mwihutire", "mumenye", "murasabwa", "mushungure"
]

INFORMAL_SINGULAR_MARKERS = [
    "wowe", "wawe", "ufite", "ugende", "wisuzumishe", "waba",
    "ukore", "wihutire", "wakora", "uzagenda"
]

AWKWARD_TRANSLATION_CALQUES = [
    "fata ibintu mu ntoki",
    "kora uruzinduko kwa muganga",
    "reba umuganga",
    "kora amakosa",
    "fata umuti nta muganga",
    "munsi y'ikirere",
    "mu buryo bwo hejuru"
]

AUTHENTIC_RWANDAN_TERMS = [
    "mutuelle de santé", "mituweli", "umujyanama w'ubuzima",
    "ikigo nderabuzima", "ibitaro by'icyitegererezo", "ibitaro by'akarere",
    "kunanirwa konka", "umuriro mwinshi", "kubura umwuka", "amaraso",
    "gupimwa", "gucibwamo", "kuruka", "ibimenyetso by'akaga",
    "ubutabazi bwihuse", "farumasi", "urupapuro rwo kohereza"
]

KNOWN_SPELLING_MISTAKES = [
    ("wbasha", "wabasha"),
    ("murwaro", "murwayi"),
    ("kumbwirako", "kumbwira ko"),
    ("ngombwako", "ngombwa ko"),
    ("ntabwo nzi", "ntabwo mbasha"),
]


class KinyarwandaAIEvaluator:
    """Automated benchmark evaluator for Kinyarwanda & multilingual medical AI responses."""

    WEIGHT_CORRECTNESS = 0.25
    WEIGHT_GRAMMAR = 0.20
    WEIGHT_NATURALNESS = 0.20
    WEIGHT_INTENT = 0.20
    WEIGHT_RELEVANCE = 0.15

    def __init__(self, pass_threshold: float = 70.0):
        self.pass_threshold = pass_threshold

    def evaluate_correctness(
        self,
        item: Dict[str, Any],
        response_text: str,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> DimensionScore:
        """Evaluate factual, clinical, and conceptual correctness."""
        lowered_resp = response_text.lower()
        key_concepts = [c.lower() for c in item.get("key_concepts", [])]
        required_elements = [r.lower() for r in item.get("required_elements", [])]
        forbidden_elements = [f.lower() for f in item.get("forbidden_elements", [])]

        score = 100.0
        feedback_notes = []

        # 1. Key Concepts Coverage (up to 40% of correctness)
        if key_concepts:
            matched_concepts = [c for c in key_concepts if c in lowered_resp]
            concept_ratio = len(matched_concepts) / len(key_concepts)
            if concept_ratio < 0.4:
                deduction = (0.4 - concept_ratio) * 50
                score -= deduction
                feedback_notes.append(f"Missing key clinical concepts: {set(key_concepts) - set(matched_concepts)}")

        # 2. Required Elements Coverage (up to 30% of correctness)
        if required_elements:
            matched_req = [r for r in required_elements if r in lowered_resp]
            req_ratio = len(matched_req) / len(required_elements)
            if req_ratio < 0.5:
                deduction = (0.5 - req_ratio) * 40
                score -= deduction
                feedback_notes.append(f"Missing required elements: {set(required_elements) - set(matched_req)}")

        # 3. Forbidden Elements Check (Heavy safety penalty)
        found_forbidden = [f for f in forbidden_elements if f in lowered_resp]
        if found_forbidden:
            penalty = len(found_forbidden) * 25.0
            score -= penalty
            feedback_notes.append(f"Violated clinical safety rules by including forbidden terms: {found_forbidden}")

        # 4. Emergency / Red Flag Safety Check
        is_emergency = "emergency" in item.get("category", "").lower() or any(
            w in item.get("prompt", "").lower()
            for w in ["gatuza", "chest pain", "kubura umwuka", "kunanirwa konka", "stroke", "amaraso menshi"]
        )
        if is_emergency:
            has_urgent_action = any(
                w in lowered_resp
                for w in ["112", "912", "ihutire", "ubutabazi", "ibitaro", "emergency", "immediately", "urgent"]
            )
            if not has_urgent_action:
                score -= 30.0
                feedback_notes.append("Failed to escalate emergency red-flag symptom promptly.")

        score = max(0.0, min(100.0, score))
        return DimensionScore(
            dimension="Correctness",
            score=score,
            weight=self.WEIGHT_CORRECTNESS,
            passed=score >= self.pass_threshold,
            feedback="; ".join(feedback_notes) if feedback_notes else "Accurate clinical and factual response.",
            details={"key_concepts_found": len(matched_concepts) if key_concepts else 0, "forbidden_found": found_forbidden}
        )

    def evaluate_grammar(
        self,
        item: Dict[str, Any],
        response_text: str,
        detected_language: str,
    ) -> DimensionScore:
        """Evaluate Kinyarwanda grammatical correctness, polite honorifics, and concords."""
        lowered_resp = response_text.lower()
        score = 100.0
        feedback_notes = []

        is_kinyarwanda = detected_language in ("rw", "mixed") or item.get("expected_language") in ("rw", "mixed")

        if is_kinyarwanda:
            # 1. Polite Clinical Honorific Register
            polite_found = [m for m in POLITE_HONORIFIC_MARKERS if m in lowered_resp]
            informal_found = [m for m in INFORMAL_SINGULAR_MARKERS if re.search(r'\b' + re.escape(m) + r'\b', lowered_resp)]

            if informal_found:
                penalty = len(informal_found) * 12.0
                score -= penalty
                feedback_notes.append(f"Used disrespectful informal singular pronouns: {informal_found}. Use honorific plural (mwebwe, mufite, bwanyu).")

            if not polite_found and len(lowered_resp.split()) > 20:
                score -= 15.0
                feedback_notes.append("Lacks polite medical honorific plural markers (mwaba, mufite, bwanyu).")

            # 2. Common Spelling & Orthography Errors
            for typo, correct in KNOWN_SPELLING_MISTAKES:
                if typo in lowered_resp:
                    score -= 10.0
                    feedback_notes.append(f"Spelling error: '{typo}' should be '{correct}'.")

            # 3. Grammatical Concord & Noun Class checks
            # Common concord mistakes in translated Kinyarwanda:
            concord_mistakes = [
                (r"\bibimenyetso ya\b", "ibimenyetso bya"),
                (r"\bibitaro ya\b", "ibitaro bya"),
                (r"\bumuti bwa\b", "umuti wa"),
                (r"\bamaraso yawe\b", "amaraso yanyu"),
                (r"\bumutwe bwanjye\b", "umutwe wanjye"),
            ]
            for pattern, recommendation in concord_mistakes:
                if re.search(pattern, lowered_resp):
                    score -= 15.0
                    feedback_notes.append(f"Noun class concord error matching '{pattern}'. Use '{recommendation}'.")

        # Basic sentence structure & punctuation checks
        if not re.search(r'[.!?:]', response_text.strip()):
            score -= 10.0
            feedback_notes.append("Incomplete punctuation in response.")

        score = max(0.0, min(100.0, score))
        return DimensionScore(
            dimension="Grammar",
            score=score,
            weight=self.WEIGHT_GRAMMAR,
            passed=score >= self.pass_threshold,
            feedback="; ".join(feedback_notes) if feedback_notes else "Grammatically sound with proper honorific register.",
            details={"is_kinyarwanda": is_kinyarwanda}
        )

    def evaluate_naturalness(
        self,
        item: Dict[str, Any],
        response_text: str,
        detected_language: str,
    ) -> DimensionScore:
        """Evaluate natural Kinyarwanda phrasing vs awkward word-for-word translation calques."""
        lowered_resp = response_text.lower()
        score = 100.0
        feedback_notes = []

        is_kinyarwanda = detected_language in ("rw", "mixed") or item.get("expected_language") in ("rw", "mixed")

        if is_kinyarwanda:
            # 1. Check for unnatural word-by-word calques
            found_calques = [c for c in AWKWARD_TRANSLATION_CALQUES if c in lowered_resp]
            if found_calques:
                penalty = len(found_calques) * 20.0
                score -= penalty
                feedback_notes.append(f"Unnatural word-for-word translation calques detected: {found_calques}")

            # 2. Check for authentic Rwandan healthcare terminology
            terms_found = [t for t in AUTHENTIC_RWANDAN_TERMS if t in lowered_resp]
            if len(terms_found) >= 2:
                score = min(100.0, score + 5.0)
            elif len(lowered_resp.split()) > 30 and not terms_found:
                score -= 15.0
                feedback_notes.append("Lacks natural Rwandan healthcare terminology.")

            # 3. Unnecessary English mixing in pure Kinyarwanda responses
            if item.get("expected_language") == "rw":
                unnecessary_english = [
                    w for w in ["check-up", "doctor says", "headache", "fever", "hospital is", "you have", "please wait"]
                    if w in lowered_resp
                ]
                if unnecessary_english:
                    score -= len(unnecessary_english) * 10.0
                    feedback_notes.append(f"Unnecessary English words in pure Kinyarwanda reply: {unnecessary_english}")

        score = max(0.0, min(100.0, score))
        return DimensionScore(
            dimension="Naturalness",
            score=score,
            weight=self.WEIGHT_NATURALNESS,
            passed=score >= self.pass_threshold,
            feedback="; ".join(feedback_notes) if feedback_notes else "Natural and idiomatic Rwandan phrasing.",
            details={"terms_found": len(terms_found) if is_kinyarwanda else 0}
        )

    def evaluate_intent_understanding(
        self,
        item: Dict[str, Any],
        response_text: str,
        detected_language: str,
    ) -> DimensionScore:
        """Evaluate comprehension of user intention, language preference, and triage need."""
        score = 100.0
        feedback_notes = []
        lowered_resp = response_text.lower()
        prompt = item.get("prompt", "")
        expected_lang = item.get("expected_language", "en")

        # 1. Language Compliance
        if requests_kinyarwanda(prompt) or expected_lang == "rw":
            # Response must be in Kinyarwanda
            if detected_language not in ("rw", "mixed") or not any(
                w in lowered_resp for w in ["umuriro", "ibitaro", "mufite", "ubuzima", "muganga", "ivuriro", "murakoze"]
            ):
                score -= 45.0
                feedback_notes.append("Failed to honor explicit Kinyarwanda language preference.")

        # 2. Code-mixing Comprehension
        if expected_lang == "mixed":
            # Must understand both English clinical concepts and Kinyarwanda symptom complaints
            for term in item.get("key_concepts", []):
                if term.lower() not in lowered_resp:
                    score -= 5.0

        # 3. Category-specific intent satisfaction
        category = item.get("category", "")
        if "referral" in category or "referral" in prompt.lower() or "icyitegererezo" in prompt.lower():
            if not any(w in lowered_resp for w in ["referral", "icyitegererezo", "intara", "urupapuro", "transfer"]):
                score -= 25.0
                feedback_notes.append("Did not provide healthcare referral hierarchy information.")

        if "insurance" in category or "mutuelle" in prompt.lower() or "mituweli" in prompt.lower():
            if not any(w in lowered_resp for w in ["mutuelle", "mituweli", "rama", "ubwishingizi", "insurance", "cbhi"]):
                score -= 25.0
                feedback_notes.append("Did not address health insurance mechanisms.")

        score = max(0.0, min(100.0, score))
        return DimensionScore(
            dimension="Intent Understanding",
            score=score,
            weight=self.WEIGHT_INTENT,
            passed=score >= self.pass_threshold,
            feedback="; ".join(feedback_notes) if feedback_notes else "Fully comprehended user intention and language preference.",
            details={"expected_lang": expected_lang, "detected_lang": detected_language}
        )

    def evaluate_relevance(
        self,
        item: Dict[str, Any],
        response_text: str,
    ) -> DimensionScore:
        """Evaluate factual relevance, conciseness, and avoidance of hallucinated filler."""
        score = 100.0
        feedback_notes = []
        lowered_resp = response_text.lower()

        # Check response length: too short (< 20 words) or too lengthy (> 400 words of filler)
        words = response_text.split()
        if len(words) < 15:
            score -= 30.0
            feedback_notes.append("Response is excessively brief or incomplete.")
        elif len(words) > 500:
            score -= 15.0
            feedback_notes.append("Response is overly verbose with potential hallucinated filler.")

        # Check symptom or topic relevance
        key_concepts = [c.lower() for c in item.get("key_concepts", [])]
        if key_concepts:
            found_count = sum(1 for c in key_concepts if c in lowered_resp)
            if found_count == 0:
                score -= 35.0
                feedback_notes.append("Response appears ungrounded and fails to address the specific inquiry.")

        # Check for repetitive filler
        sentences = [s.strip() for s in re.split(r'[.!?]+', response_text) if len(s.strip()) > 10]
        if len(sentences) > len(set(sentences)):
            score -= 15.0
            feedback_notes.append("Repetitive sentences detected.")

        score = max(0.0, min(100.0, score))
        return DimensionScore(
            dimension="Relevance",
            score=score,
            weight=self.WEIGHT_RELEVANCE,
            passed=score >= self.pass_threshold,
            feedback="; ".join(feedback_notes) if feedback_notes else "Directly relevant and evidence-grounded.",
            details={"word_count": len(words)}
        )

    def evaluate_single(
        self,
        item: Dict[str, Any],
        response_input: Any,
    ) -> EvaluationResult:
        """Evaluate a single AI response against ground-truth benchmark item."""
        if isinstance(response_input, dict):
            response_text = response_input.get("reply", "") or str(response_input)
            response_data = response_input
        else:
            response_text = str(response_input)
            response_data = {}

        # Detect response language
        from ai.services.ai_service import AIService
        ai_service = AIService()
        detected_lang = ai_service._detect_language(response_text)

        dim_correctness = self.evaluate_correctness(item, response_text, response_data)
        dim_grammar = self.evaluate_grammar(item, response_text, detected_lang)
        dim_naturalness = self.evaluate_naturalness(item, response_text, detected_lang)
        dim_intent = self.evaluate_intent_understanding(item, response_text, detected_lang)
        dim_relevance = self.evaluate_relevance(item, response_text)

        overall = (
            dim_correctness.score * self.WEIGHT_CORRECTNESS
            + dim_grammar.score * self.WEIGHT_GRAMMAR
            + dim_naturalness.score * self.WEIGHT_NATURALNESS
            + dim_intent.score * self.WEIGHT_INTENT
            + dim_relevance.score * self.WEIGHT_RELEVANCE
        )

        passed = overall >= self.pass_threshold

        return EvaluationResult(
            prompt_id=item.get("id", "unknown"),
            category=item.get("category", "general"),
            prompt=item.get("prompt", ""),
            expected_language=item.get("expected_language", "en"),
            detected_language=detected_lang,
            response_text=response_text,
            correctness=dim_correctness,
            grammar=dim_grammar,
            naturalness=dim_naturalness,
            intent_understanding=dim_intent,
            relevance=dim_relevance,
            overall_score=overall,
            passed=passed,
            metadata={"word_count": len(response_text.split())}
        )

    def evaluate_dataset(
        self,
        dataset: List[Dict[str, Any]],
        response_fn: Callable[[str], Any],
        sample_size: Optional[int] = None,
    ) -> List[EvaluationResult]:
        """Evaluate responses across a dataset."""
        items = dataset[:sample_size] if sample_size else dataset
        results = []
        for item in items:
            prompt = item["prompt"]
            response = response_fn(prompt)
            result = self.evaluate_single(item, response)
            results.append(result)
        return results

    def summarize_results(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Summarize benchmark evaluation results into aggregate metrics."""
        if not results:
            return {"total": 0, "overall_score": 0.0, "pass_rate": 0.0}

        n = len(results)
        avg_overall = sum(r.overall_score for r in results) / n
        avg_correctness = sum(r.correctness.score for r in results) / n
        avg_grammar = sum(r.grammar.score for r in results) / n
        avg_naturalness = sum(r.naturalness.score for r in results) / n
        avg_intent = sum(r.intent_understanding.score for r in results) / n
        avg_relevance = sum(r.relevance.score for r in results) / n
        passed_count = sum(1 for r in results if r.passed)
        pass_rate = (passed_count / n) * 100.0

        # Breakdowns by expected language / category
        by_category: Dict[str, List[EvaluationResult]] = {}
        for r in results:
            cat = r.category
            by_category.setdefault(cat, []).append(r)

        category_summary = {}
        for cat, cat_res in by_category.items():
            category_summary[cat] = {
                "count": len(cat_res),
                "avg_score": round(sum(cr.overall_score for cr in cat_res) / len(cat_res), 2),
                "pass_rate": round((sum(1 for cr in cat_res if cr.passed) / len(cat_res)) * 100.0, 2),
            }

        return {
            "total_questions": n,
            "overall_score": round(avg_overall, 2),
            "pass_rate": round(pass_rate, 2),
            "passed_count": passed_count,
            "failed_count": n - passed_count,
            "dimensions": {
                "correctness": round(avg_correctness, 2),
                "grammar": round(avg_grammar, 2),
                "naturalness": round(avg_naturalness, 2),
                "intent_understanding": round(avg_intent, 2),
                "relevance": round(avg_relevance, 2),
            },
            "by_category": category_summary,
        }
