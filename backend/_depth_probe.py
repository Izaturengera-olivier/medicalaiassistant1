"""THROWAWAY probe: measures real reply depth against the live provider. Delete after use.

Usage:
  ./.venv/Scripts/python.exe _depth_probe.py measure   # offline prompt/evidence sizing only
  ./.venv/Scripts/python.exe _depth_probe.py before    # 2 live calls with the OLD prompts
  ./.venv/Scripts/python.exe _depth_probe.py after     # 3 live calls with the NEW prompts
"""

import os
import re
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# The Windows console defaults to cp1252 and crashes on model output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402

import ai.providers as providers  # noqa: E402
from ai.services import ai_service as svc  # noqa: E402

CASES = {
    "patient_en": {
        "mode": "patient",
        "message": (
            "I have had a headache for three days and my neck feels stiff, "
            "what could it be and how serious is it?"
        ),
    },
    "patient_rw": {
        "mode": "patient",
        "message": "Mfite umuriro iminsi itatu n'ibizunguzungu, birakabije?",
    },
    "professional_en": {
        "mode": "professional",
        "message": (
            "65F, epigastric pain 3 weeks, weight loss, no alarm features "
            "documented - differential and workup?"
        ),
    },
}

# Verbatim pre-change reply descriptions, so the "before" run is a fair comparison.
OLD_REPLY_DESCRIPTIONS = {
    "patient": "conversational reply to the patient, including any follow-up questions",
    "professional": "clinician-level conversational answer, short paragraphs or tight bullets",
}

MARKDOWN_PATTERNS = {
    "bold/italic **": r"\*\*",
    "single asterisk *": r"(?<![*\w])\*(?!\s)",
    "heading #": r"(?m)^\s*#{1,6}\s",
    "backtick": r"`",
    "pipe table": r"(?m)^\s*\|.*\|",
    "html tag": r"</?[a-zA-Z]+>",
    "link [x](y)": r"\[[^\]\n]+\]\([^)\n]+\)",
    "code fence": r"```",
}

CALLS = []
REAL_POST = providers.requests.post


def instrumented_post(url, headers=None, json=None, timeout=None):
    """Record finish_reason/usage/status for the probe. Never touches the key."""
    body = json or {}
    record = {
        "model": body.get("model"),
        "max_tokens": body.get("max_tokens"),
        "prompt_chars": sum(len(m.get("content", "")) for m in body.get("messages", [])),
    }
    try:
        response = REAL_POST(url, headers=headers, json=json, timeout=timeout)
    except Exception as exc:  # pragma: no cover - probe only
        record["exception"] = repr(exc)
        CALLS.append(record)
        raise
    record["status"] = response.status_code
    if response.status_code == 200:
        payload = response.json()
        usage = payload.get("usage") or {}
        choice = (payload.get("choices") or [{}])[0]
        record.update(
            {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "finish_reason": (choice.get("message") or {}).get("finish_reason")
                or choice.get("finish_reason"),
            }
        )
    else:
        record["error_body"] = response.text[:400]
    CALLS.append(record)
    return response


def analyze(reply):
    words = len(reply.split())
    md = {name: len(re.findall(pat, reply)) for name, pat in MARKDOWN_PATTERNS.items()}
    md = {k: v for k, v in md.items() if v}
    cites = re.findall(r"\[\d+\]", reply)
    sections = [line for line in reply.split("\n") if line.strip() and len(line.strip()) < 60 and not line.strip().startswith("-")]
    return {
        "words": words,
        "markdown": md,
        "inline_citations": len(cites),
        "distinct_lines_pct": round(
            100 * len(set(reply.split("\n"))) / max(1, len(reply.split("\n"))), 1
        ),
    }


def _call_through_service(service, case, message):
    if case["mode"] == "patient":
        return service.converse(message)
    return service.converse_professional(message)


def run_case(key, case, old=False):
    service = svc.AIService()
    message = case["message"]
    language = service._detect_language(message, [])
    evidence = service._retrieve_evidence(service._build_query([], message))
    evidence_block = service.retrieval_service.format_evidence_for_ai(evidence)

    if old:
        schema = dict(
            svc.CONVERSATION_SCHEMA if case["mode"] == "patient" else svc.PROFESSIONAL_SCHEMA
        )
        schema["reply"] = OLD_REPLY_DESCRIPTIONS[case["mode"]]
        monkey_patch(service, case["mode"], language, evidence_block, schema)
    else:
        schema = svc.CONVERSATION_SCHEMA if case["mode"] == "patient" else svc.PROFESSIONAL_SCHEMA

    print(f"\n=== {key} ({'BEFORE' if old else 'AFTER'}) ===")
    print(
        f"evidence passages: {len(evidence)} | evidence_block chars: {len(evidence_block)} "
        f"| system+schema prompt chars: {len(evidence_block)}+"
    )
    if old:
        messages = (
            service._build_messages(message, [], None, None, evidence, language)
            if case["mode"] == "patient"
            else service._build_professional_messages(message, [], None, evidence, language)
        )
        provider = providers.get_llm_provider(
            service.provider_name,
            api_key=service.api_key,
            model=service.model,
            base_url=service.base_url,
        )
        raw = provider.complete_structured(messages, schema)
        result = service._normalize_result(raw, evidence)
    else:
        result = _call_through_service(service, case, message)
        if result["model_used"] == "mock" and CALLS and CALLS[-1].get("status") == 429:
            print("       (429 seen -> waiting 90s and retrying once through the same path)")
            time.sleep(90)
            result = _call_through_service(service, case, message)

    reply = result["reply"]
    stats = analyze(reply)
    print(f"model_used           : {result['model_used']}")
    print(f"reply word count     : {stats['words']}")
    print(f"inline citations     : {stats['inline_citations']}")
    print(f"markdown leaks       : {stats['markdown'] or 'none'}")
    print(f"sources returned     : {len(result['sources'])}")
    print(f"urgency              : {result['urgency_level']}")
    print(f"follow-ups           : {len(result['follow_up_questions'])}")
    print("--- reply ---")
    print(reply)
    print("--- end reply ---")
    print("--- provider calls for this case ---")
    global _MARK
    for call in CALLS[_MARK:]:
        print(call)
    _MARK = len(CALLS)
    return stats


def monkey_patch(service, mode, language, evidence_block, schema):
    """Restore the pre-change prompt + schema description for a fair baseline."""
    from ai.services import prompts as p

    if mode == "patient":
        def old_prompt(evidence_block="", patient_context=None, language="en"):
            prompt = p.get_system_prompt() + """

CONVERSATION MODE:
- You are having an ongoing conversation with a patient. Reply conversationally, in clear, concise paragraphs.
- Begin by directly addressing the patient's latest message. Do not use a generic health disclaimer or generic symptom script when the message is specific.
- Use all relevant details from the latest message, prior user turns, patient context, and retrieved evidence. Never ignore a symptom, question, medication, duration, severity, or language supplied by the patient.
- If the latest message is unclear or incomplete, say exactly what is unclear and ask one focused clarification question instead of guessing.
- Ground every medical statement in the TRUSTED EVIDENCE below. If it does not cover something, say so and advise professional care.
- Cite evidence inline by its number, e.g. [1]. NEVER invent sources, links, guidelines, dosages, or numbers.
- Ask up to 3 focused follow-up questions per reply whenever information is missing. Never repeat a question the patient has already answered.
- Before answering, review and compare the retrieved evidence against the patient's full message and conversation history. Provide only the concise conclusion, uncertainty, safety reasoning, and citations.
- Reply in the exact same language the patient writes in (English or Kinyarwanda).
- If warning signs are present, put the urgent advice FIRST in plain language.
"""
            prompt += f"""
{p.get_language_rule(language)}

TRUSTED EVIDENCE (approved medical sources):
{evidence_block or "No relevant evidence found in the approved sources."}"""
            return prompt

        svc.get_chat_system_prompt = old_prompt
    else:
        def old_prof_prompt(evidence_block="", professional_context=None, language="en"):
            prompt = """You are an advanced clinical decision support AI assistant inside a healthcare system, talking WITH a licensed clinician (doctor or pharmacist), not with a patient.

CRITICAL SAFETY RULES:
1. NEVER claim certainty when evidence is uncertain; state your confidence and why.
2. NEVER invent medications, dosages, interactions, guidelines, statistics, or sources.
3. ALWAYS cite retrieved evidence inline by its number, e.g. [1], and say clearly when the approved sources do not cover something.
4. ALWAYS distinguish "supported by the retrieved evidence" from "general clinical knowledge".
5. ALWAYS flag red flags / contraindications / dangerous interactions when the case contains them.
6. NEVER output a definitive diagnosis or a prescription order - present options, rationale, and trade-offs for the clinician to decide.
7. Reply in the exact same language the clinician writes in (English or Kinyarwanda).

PROFESSIONAL MODE:
- Answer at clinician level: mechanisms, differentials, dosing considerations, interactions, monitoring, and guideline-based steps are all appropriate to discuss.
- Be direct, highly intelligent, and concise. Short paragraphs or tight bullet lists. No patient-directed soothing language; you are talking to a peer.
- When information about the case is missing, say exactly what would change your answer (max 3 items).
- Ground every medical statement in the TRUSTED EVIDENCE below. If it does not cover something, say so plainly and answer from general clinical knowledge only when clearly labeled as such.
"""
            prompt += f"""
{p.get_language_rule(language)}

TRUSTED EVIDENCE (approved medical sources):
{evidence_block or "No relevant evidence found in the approved sources."}"""
            return prompt

        svc.get_professional_system_prompt = old_prof_prompt

    svc._ORIGINAL_SCHEMA = schema


def measure():
    service = svc.AIService()
    doc_chars = [len(item["content"]) for item in service._retrieve_evidence("fever", )]
    print(f"MAX_EVIDENCE_RESULTS={service.MAX_EVIDENCE_RESULTS} "
          f"EVIDENCE_CONTENT_CHARS={service.retrieval_service.EVIDENCE_CONTENT_CHARS} "
          f"DEFAULT_MAX_TOKENS={providers.DEFAULT_MAX_TOKENS}")
    for key, case in CASES.items():
        message = case["message"]
        language = service._detect_language(message, [])
        evidence = service._retrieve_evidence(service._build_query([], message))
        block = service.retrieval_service.format_evidence_for_ai(evidence)
        if case["mode"] == "patient":
            messages = service._build_messages(message, [], None, None, evidence, language)
        else:
            messages = service._build_professional_messages(message, [], None, evidence, language)
        chars = sum(len(m["content"]) for m in messages)
        schema = svc.CONVERSATION_SCHEMA if case["mode"] == "patient" else svc.PROFESSIONAL_SCHEMA
        import json as _json
        total = chars + len(_json.dumps(schema, ensure_ascii=False))
        print(f"{key}: passages={len(evidence)} block_chars={len(block)} "
              f"full_prompt_chars={total} ~tokens={total // 4}")
        print("   titles:", [e["title"][:38] for e in evidence])


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "after"
    print(f"provider={settings.AI_PROVIDER} model={settings.AI_MODEL} "
          f"base_url={settings.AI_BASE_URL} key_configured={bool(settings.AI_API_KEY)}")

    if mode == "measure":
        measure()
        return

    providers.requests.post = instrumented_post

    if mode == "before":
        targets = [(k, c, True) for k, c in CASES.items()]
    elif mode == "before_rw":
        targets = [("patient_rw", CASES["patient_rw"], True)]
    else:
        targets = [(k, c, False) for k, c in CASES.items()]

    for i, (key, case, old) in enumerate(targets):
        if i:
            time.sleep(90)  # stay under the shared 8000 TPM Groq budget
        try:
            run_case(key, case, old=old)
        except Exception as exc:
            print(f"{key}: ERROR {type(exc).__name__}: {exc}")

    print("\n=== provider call log (no secrets) ===")
    for call in CALLS:
        print(call)


main()
