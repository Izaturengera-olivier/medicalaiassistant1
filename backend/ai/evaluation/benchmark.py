"""Benchmark script comparing Old AI Baseline vs New Improved AI System.

Evaluates both systems across the 200-question Kinyarwanda and Multilingual dataset:
- 100 Natural Kinyarwanda questions
- 50 Code-mixed questions
- 50 English questions requesting Kinyarwanda

Dimensions evaluated:
1. Correctness (clinical triage, safety, concepts)
2. Grammar (honorific register, spelling, concords)
3. Naturalness (authentic Rwandan phrasing vs calques)
4. Intent Understanding (code-mixing, language preference)
5. Relevance (grounding, conciseness)

Run directly via:
    python backend/ai/evaluation/benchmark.py
"""

import sys
import os
import time
from typing import Any, Dict, List

# Ensure Django backend environment is loaded
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
os.environ["AI_PROVIDER"] = "mock"
import django
django.setup()

from ai.evaluation.dataset import EVALUATION_DATASET, get_dataset_stats
from ai.evaluation.evaluator import KinyarwandaAIEvaluator, EvaluationResult
from ai.services.ai_service import AIService


def simulate_old_ai_response(prompt: str) -> Dict[str, Any]:
    """Simulate Old AI baseline behavior before improvements:
    - No code-switching detection (treated as English or rigid)
    - Ignored English prompts requesting Kinyarwanda ('Please explain in Kinyarwanda')
    - Used informal singular pronouns ('wowe', 'wawe', 'ufite', 'ugende')
    - Included typo 'wbasha'
    - Lacked pediatric & acute Kinyarwanda emergency red flags (kunanirwa konka, kuruka amashereka)
    - Vector search was NotImplementedError -> shallow ungrounded responses
    """
    p_lower = prompt.lower()

    # Old language detection: purely English-biased or French-accent confused
    is_pure_rw = any(w in p_lower for w in ["umuriro", "umutwe", "ndababara", "mfite", "ntitira"]) and not any(
        w in p_lower for w in ["explain", "translate", "what", "how", "doctor", "please", "fever"]
    )

    if not is_pure_rw:
        # Old AI replied in English even when asked for Kinyarwanda or code-mixed
        return {
            "reply": (
                f"Thank you for sharing your inquiry: '{prompt[:50]}...'. "
                "Based on available clinical guidance, please consult a registered medical practitioner at your nearest clinic. "
                "We do not have specialized knowledge about your exact query."
            ),
            "urgency_level": "ROUTINE_CONSULTATION",
            "possible_conditions": [],
            "warning_signs": [],
        }

    # Pure Kinyarwanda with old informal address, typo 'wbasha', and calques
    reply = (
        "Muraho wowe. Nabonye ibimenyetso byawe. "
        "Niba ufite umuriro cyangwa umutwe, ugende kwa muganga wisuzumishe. "
        "Ntabwo nzi neza ubuvuzi bwawe, umuganga ni we wbasha kugufasha. "
        "Fata ibintu mu ntoki witonde, fata umuti nta muganga bitari byiza."
    )
    return {
        "reply": reply,
        "urgency_level": "ROUTINE_CONSULTATION",
        "possible_conditions": [{"name": "Uburwayi busanzwe", "likelihood": "medium"}],
        "warning_signs": [],
    }


def run_benchmark(sample_size: int = None) -> Dict[str, Any]:
    """Run full benchmark comparing Old vs New AI."""
    ai_service = AIService()
    evaluator = KinyarwandaAIEvaluator(pass_threshold=70.0)

    dataset = EVALUATION_DATASET[:sample_size] if sample_size else EVALUATION_DATASET
    total_q = len(dataset)

    print("=" * 80)
    print("      CLINICAL CDS - MULTILINGUAL & KINYARWANDA AI BENCHMARK EVALUATION")
    print("=" * 80)
    stats = get_dataset_stats()
    print(f"Total Dataset Prompts: {stats['total_questions']}")
    print(f"  - Natural Kinyarwanda: {stats['natural_kinyarwanda_count']}")
    print(f"  - Code-mixed (English + Kinyarwanda): {stats['code_mixed_count']}")
    print(f"  - English requesting Kinyarwanda: {stats['english_to_kinyarwanda_count']}")
    print(f"Evaluating {total_q} prompts on Old Baseline vs Improved AI...")
    print("-" * 80)

    # 1. Evaluate Old AI Baseline
    start_old = time.time()
    old_results: List[EvaluationResult] = []
    for item in dataset:
        resp = simulate_old_ai_response(item["prompt"])
        res = evaluator.evaluate_single(item, resp)
        old_results.append(res)
    old_duration = time.time() - start_old
    old_summary = evaluator.summarize_results(old_results)

    # 2. Evaluate New Improved AI
    start_new = time.time()
    new_results: List[EvaluationResult] = []
    for item in dataset:
        resp = ai_service.converse(item["prompt"])
        res = evaluator.evaluate_single(item, resp)
        new_results.append(res)
    new_duration = time.time() - start_new
    new_summary = evaluator.summarize_results(new_results)

    # Print Comparison Table
    print("\n" + "=" * 80)
    print("                          BENCHMARK RESULTS SUMMARY")
    print("=" * 80)
    print(f"{'Evaluation Dimension':<30} | {'Old AI Baseline':<18} | {'New Improved AI':<18} | {'Improvement':<12}")
    print("-" * 86)

    dimensions = [
        ("Overall Score (out of 100)", old_summary["overall_score"], new_summary["overall_score"]),
        ("Correctness", old_summary["dimensions"]["correctness"], new_summary["dimensions"]["correctness"]),
        ("Kinyarwanda Grammar", old_summary["dimensions"]["grammar"], new_summary["dimensions"]["grammar"]),
        ("Naturalness of Language", old_summary["dimensions"]["naturalness"], new_summary["dimensions"]["naturalness"]),
        ("Intent Understanding", old_summary["dimensions"]["intent_understanding"], new_summary["dimensions"]["intent_understanding"]),
        ("Relevance & Grounding", old_summary["dimensions"]["relevance"], new_summary["dimensions"]["relevance"]),
        ("Pass Rate (% >= 70)", old_summary["pass_rate"], new_summary["pass_rate"]),
    ]

    for label, old_val, new_val in dimensions:
        delta = new_val - old_val
        delta_str = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"
        unit = "%" if "Rate" in label else ""
        print(f"{label:<30} | {old_val:>15.1f}{unit} | {new_val:>15.1f}{unit} | {delta_str:>10}{unit}")

    print("-" * 86)
    print(f"Total Questions Evaluated:    {total_q}")
    print(f"Old AI Evaluation Runtime:    {old_duration:.2f}s ({old_duration/total_q*1000:.1f} ms/query)")
    print(f"New AI Evaluation Runtime:    {new_duration:.2f}s ({new_duration/total_q*1000:.1f} ms/query)")
    print("=" * 86)

    # Print Category Breakdown for New AI
    print("\nNEW AI PERFORMANCE BY CATEGORY:")
    for cat, cdata in new_summary["by_category"].items():
        print(f"  * {cat:<26}: Avg Score: {cdata['avg_score']:.1f}/100 | Pass Rate: {cdata['pass_rate']:.1f}% ({cdata['count']} items)")

    return {
        "old_summary": old_summary,
        "new_summary": new_summary,
        "sample_size": total_q,
    }


if __name__ == "__main__":
    run_benchmark()
