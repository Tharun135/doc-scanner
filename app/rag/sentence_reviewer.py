"""
sentence_reviewer.py
=====================
Core sentence-level RAG review pipeline for DocScanner.

Architecture (privacy-first):
    Document
        ↓
    Sentence segmentation (spaCy)  [already done upstream]
        ↓
    For each sentence:
        Sentence
            ↓
        Rule classifier (lightweight keyword tagger)
            ↓
        Retrieve relevant style rules (RuleVectorStore — LOCAL ChromaDB)
            ↓
        Reranker (CrossEncoder — LOCAL sentence-transformers)
            ↓
        LLM evaluator — priority order:
            1. Ollama (LOCAL — nothing leaves machine)  ← DEFAULT
            2. Gemini (cloud — only if no Ollama + key set)
            3. Retrieval-only heuristic (no LLM at all)
        ↓
    Structured feedback
"""

import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional reranker
# ---------------------------------------------------------------------------
try:
    from sentence_transformers import CrossEncoder
    _RERANKER: Optional[CrossEncoder] = None
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    _RERANKER = None

_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def _get_reranker() -> Optional[Any]:
    global _RERANKER
    if RERANKER_AVAILABLE and _RERANKER is None:
        try:
            _RERANKER = CrossEncoder(_RERANKER_MODEL)
            logger.info(f"[SentenceReviewer] Reranker loaded: {_RERANKER_MODEL}")
        except Exception as exc:
            logger.warning(f"[SentenceReviewer] Reranker load failed: {exc}")
    return _RERANKER


# ---------------------------------------------------------------------------
# Rule classifier: lightweight keyword tagger
# ---------------------------------------------------------------------------

# Maps surface patterns → rule category hint used to focus retrieval
_CLASSIFIER_PATTERNS: List[Dict[str, Any]] = [
    # Passive voice
    {"pattern": re.compile(r"\b(is|are|was|were|has been|have been|being|to be)\s+\w+(ed|en)\b", re.I),
     "category": "grammar", "hint": "passive voice"},
    # Future tense
    {"pattern": re.compile(r"\b(shall|going to)\b", re.I),
     "category": "tense", "hint": "future tense avoid shall"},
    # Modal verbs
    {"pattern": re.compile(r"\b(may|could|might|should|would)\b", re.I),
     "category": "tense", "hint": "modal verb clarity"},
    # UI bad patterns
    {"pattern": re.compile(r"\bclick\s+on\b|\bclick\s+the\s+\w+\s+button\b", re.I),
     "category": "ui-label", "hint": "UI label click on button"},
    # First person
    {"pattern": re.compile(r"\b(I|my|me)\b", re.I),
     "category": "voice", "hint": "first person pronoun"},
    # Non-imperative step start
    {"pattern": re.compile(r"^(To|In order to|For)\s+\w+", re.I),
     "category": "voice", "hint": "imperative voice instruction"},
    # Reduplication adverbs
    {"pattern": re.compile(r"\b(simply|easily|quickly|basically|really|extremely|actually|just)\b", re.I),
     "category": "adverb", "hint": "weak adverb precision"},
    # Contractions
    {"pattern": re.compile(r"\b(don't|doesn't|won't|can't|shouldn't|isn't|aren't|haven't|hasn't|wouldn't)\b", re.I),
     "category": "formality", "hint": "contraction formal writing"},
    # Jargon
    {"pattern": re.compile(r"\b(utilize|leverage|facilitate|synergy|paradigm|robust)\b", re.I),
     "category": "clarity", "hint": "jargon corporate word"},
    # Phrasal verbs
    {"pattern": re.compile(r"\b(set up|shut down|turn on|turn off|log in|log out|back up|carry out)\b", re.I),
     "category": "phrasal-verb", "hint": "phrasal verb localization"},
    # Gender
    {"pattern": re.compile(r"\b(he|him|his|she|her|hers|mankind|manmade|man-hours)\b", re.I),
     "category": "inclusivity", "hint": "gender neutral inclusive language"},
    # Vague terms
    {"pattern": re.compile(r"\b(stuff|things|something|somehow|somewhat|etc\.?)\b", re.I),
     "category": "clarity", "hint": "vague imprecise term"},
    # Idioms
    {"pattern": re.compile(r"\b(at the end of the day|in a nutshell|ballpark)\b", re.I),
     "category": "translation", "hint": "idiom localization"},
]


def classify_sentence(sentence: str) -> List[Dict[str, str]]:
    """
    Lightweight rule classifier.
    Returns list of {category, hint} dicts for patterns matched in the sentence.
    """
    matched = []
    seen_categories: set = set()
    for entry in _CLASSIFIER_PATTERNS:
        if entry["pattern"].search(sentence):
            cat = entry["category"]
            if cat not in seen_categories:
                matched.append({"category": cat, "hint": entry["hint"]})
                seen_categories.add(cat)
    return matched


# ---------------------------------------------------------------------------
# Retrieval with optional reranking
# ---------------------------------------------------------------------------

def retrieve_and_rerank(
    sentence: str,
    categories: List[str],
    top_k_retrieve: int = 10,
    top_k_final: int = 3,
) -> List[Dict[str, Any]]:
    """
    1. Query RuleVectorStore for top_k_retrieve candidate rules.
    2. Optionally rerank with CrossEncoder and return top_k_final.

    Args:
        sentence:        The sentence being evaluated.
        categories:      List of rule categories to narrow retrieval (empty = all).
        top_k_retrieve:  Candidates fetched from vector store.
        top_k_final:     Rules returned after reranking.

    Returns:
        List of rule dicts sorted by relevance.
    """
    from app.rag.rule_vectorstore import get_rule_vectorstore

    store = get_rule_vectorstore()
    if not store.is_ready():
        return []

    # If we have category hints, do one targeted query per category and merge
    all_rules: Dict[str, Dict[str, Any]] = {}

    if categories:
        for cat in categories:
            rules = store.retrieve_rules(sentence, top_k=top_k_retrieve, category_filter=cat)
            for r in rules:
                rid = r["rule_id"]
                # Prefer higher score if same rule appears via multiple category queries
                if rid not in all_rules or r["score"] > all_rules[rid]["score"]:
                    all_rules[rid] = r
        # Also do an uncategorized query so we don't miss cross-category rules
        uncategorized = store.retrieve_rules(sentence, top_k=top_k_retrieve)
        for r in uncategorized:
            rid = r["rule_id"]
            if rid not in all_rules or r["score"] > all_rules[rid]["score"]:
                all_rules[rid] = r
    else:
        rules = store.retrieve_rules(sentence, top_k=top_k_retrieve)
        for r in rules:
            all_rules[r["rule_id"]] = r

    candidates = list(all_rules.values())

    if not candidates:
        return []

    # --- Reranking ---
    reranker = _get_reranker()
    if reranker and len(candidates) > top_k_final:
        try:
            pairs = [(sentence, r["embed_text"]) for r in candidates]
            scores = reranker.predict(pairs)
            for rule, score in zip(candidates, scores):
                rule["rerank_score"] = float(score)
            candidates.sort(key=lambda r: r.get("rerank_score", r["score"]), reverse=True)
            logger.debug(f"[SentenceReviewer] Reranker applied — top rule: {candidates[0]['rule_id']}")
        except Exception as exc:
            logger.warning(f"[SentenceReviewer] Reranker failed: {exc} — using vector scores")
            candidates.sort(key=lambda r: r["score"], reverse=True)
    else:
        candidates.sort(key=lambda r: r["score"], reverse=True)

    return candidates[:top_k_final]


# ---------------------------------------------------------------------------
# LLM backends  (privacy-first: Ollama local → Gemini cloud → none)
# ---------------------------------------------------------------------------

_OLLAMA_URL = "http://localhost:11434/api/generate"
_OLLAMA_MODELS = ["phi3:mini", "phi3", "llama3", "mistral", "gemma"]


def _call_ollama(prompt: str) -> Optional[str]:
    """
    Call local Ollama LLM. No data leaves the machine.
    Tries common models in order until one responds.
    """
    try:
        import requests
        # Pick the model to use — respect env var override
        model = os.environ.get("OLLAMA_MODEL") or None

        if model is None:
            # Auto-detect which model is installed
            try:
                tags_resp = requests.get("http://localhost:11434/api/tags", timeout=3)
                if tags_resp.status_code == 200:
                    installed = [m["name"] for m in tags_resp.json().get("models", [])]
                    for candidate in _OLLAMA_MODELS:
                        if any(candidate in inst for inst in installed):
                            model = candidate
                            break
            except Exception:
                pass
            model = model or _OLLAMA_MODELS[0]  # fallback to first candidate

        response = requests.post(
            _OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 300, "num_ctx": 1500},
            },
            timeout=60,
        )
        if response.status_code == 200:
            text = response.json().get("response", "").strip()
            if text:
                logger.info(f"[SentenceReviewer] Ollama ({model}) response OK")
                return text
        logger.warning(f"[SentenceReviewer] Ollama HTTP {response.status_code}")
        return None
    except Exception as exc:
        logger.debug(f"[SentenceReviewer] Ollama unavailable: {exc}")
        return None


def _call_gemini(prompt: str) -> Optional[str]:
    """Call Google Gemini API (cloud). Sends the sentence + rules to Google."""
    try:
        import google.generativeai as genai

        api_key = (
            os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )
        if not api_key:
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=300,
            ),
        )
        logger.info("[SentenceReviewer] Gemini (cloud) response OK")
        return response.text.strip()
    except ImportError:
        logger.warning("[SentenceReviewer] google-generativeai not installed")
        return None
    except Exception as exc:
        logger.error(f"[SentenceReviewer] Gemini call failed: {exc}")
        return None


def _call_llm(prompt: str) -> tuple:
    """
    Privacy-first LLM dispatch.
    Returns (response_text, backend_name) where backend_name is one of:
      'ollama'  — local, data stays on machine
      'gemini'  — cloud, sentence is sent to Google
      None      — no LLM available

    Priority:
      1. Ollama (local) — always tried first
      2. Gemini (cloud) — only if GOOGLE_API_KEY is set AND use_cloud_llm is allowed
    """
    # 1. Try Ollama first (local, private)
    result = _call_ollama(prompt)
    if result:
        return result, "ollama"

    # 2. Try Gemini (cloud) — only if env var explicitly permits
    allow_cloud = os.environ.get("ALLOW_CLOUD_LLM", "true").lower() != "false"
    if allow_cloud:
        result = _call_gemini(prompt)
        if result:
            return result, "gemini"

    return None, None



def _build_review_prompt(sentence: str, rules: List[Dict[str, Any]]) -> str:
    """
    Build a structured prompt that makes Gemini act as a documentation linter.
    """
    if not rules:
        rules_text = "No specific rules retrieved — apply general technical writing standards."
    else:
        rule_lines = []
        for i, r in enumerate(rules, 1):
            rule_lines.append(
                f"{i}. [{r['rule_id']} | {r['category']} | severity: {r['severity']}]\n"
                f"   Rule: {r['message']}\n"
                f"   Guidance: {r['suggestion']}\n"
                f"   Bad: {r['example_violation']}\n"
                f"   Good: {r['example_correction']}"
            )
        rules_text = "\n\n".join(rule_lines)

    prompt = f"""You are a technical writing reviewer for industry-standard industrial documentation.

Your task is to evaluate the sentence below against the provided style guide rules.

SENTENCE TO REVIEW:
"{sentence}"

STYLE GUIDE RULES:
{rules_text}

INSTRUCTIONS:
- If the sentence violates one or more of the rules above, report the most important violation.
- If the sentence is compliant, say so clearly.
- Do not invent violations not supported by the rules.
- Keep the suggested rewrite concise and direct.
- Preserve technical terms, product names, and UI labels exactly.

Respond with EXACTLY this JSON format (no markdown, no extra text):
{{
  "compliant": true or false,
  "rule_id": "RULE_XYZ or null if compliant",
  "violation": "short name of violation or null",
  "explanation": "one concise sentence explaining the problem",
  "suggestion": "the corrected sentence, or the original if compliant",
  "severity": "error | warn | info | ok"
}}"""
    return prompt


def _call_gemini(prompt: str) -> Optional[str]:
    """Call Google Gemini API and return the raw text response."""
    try:
        import google.generativeai as genai

        api_key = (
            os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )
        if not api_key:
            logger.warning("[SentenceReviewer] No Gemini API key found in environment")
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=300,
            ),
        )
        return response.text.strip()
    except ImportError:
        logger.warning("[SentenceReviewer] google-generativeai not installed")
        return None
    except Exception as exc:
        logger.error(f"[SentenceReviewer] Gemini call failed: {exc}")
        return None


def _parse_llm_response(raw: str, sentence: str, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse Gemini JSON response. Falls back to a rule-based result on parse failure.
    """
    import json as _json

    # Strip markdown fences if present
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.M)

    try:
        data = _json.loads(cleaned)
        return {
            "compliant": bool(data.get("compliant", True)),
            "rule_id": data.get("rule_id"),
            "violation": data.get("violation"),
            "explanation": data.get("explanation", ""),
            "suggestion": data.get("suggestion", sentence),
            "severity": data.get("severity", "warn"),
            # No hardcoded 'rag_gemini' here — let the caller add it
        }
    except Exception:
        logger.warning(f"[SentenceReviewer] Failed to parse LLM JSON: {raw[:200]}")
        # Fallback: use top rule metadata
        if rules:
            top = rules[0]
            return {
                "compliant": False,
                "rule_id": top["rule_id"],
                "violation": top["category"],
                "explanation": top["message"],
                "suggestion": top["example_correction"] or sentence,
                "severity": top["severity"],
                "method": "rag_fallback",
            }
        return {
            "compliant": True,
            "rule_id": None,
            "violation": None,
            "explanation": "Could not parse LLM response.",
            "suggestion": sentence,
            "severity": "ok",
            "method": "parse_error",
        }


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def review_sentence(
    sentence: str,
    top_k_retrieve: int = 10,
    top_k_final: int = 3,
    use_llm: bool = True,
) -> Dict[str, Any]:
    """
    Full pipeline: classify → retrieve → rerank → LLM evaluate.

    Args:
        sentence:         A single sentence from the document.
        top_k_retrieve:   Candidates fetched from vector store.
        top_k_final:      Rules sent to LLM after reranking.
        use_llm:          If False, return retrieval results only (faster, no API call).

    Returns:
        Structured feedback dict.
    """
    sentence = sentence.strip()
    if not sentence:
        return {
            "sentence": sentence,
            "compliant": True,
            "rule_id": None,
            "violation": None,
            "explanation": "Empty sentence.",
            "suggestion": sentence,
            "severity": "ok",
            "method": "skip_empty",
        }

    # Step 1: Classify
    classifications = classify_sentence(sentence)
    categories = list({c["category"] for c in classifications})
    hints = [c["hint"] for c in classifications]
    logger.debug(f"[SentenceReviewer] Classified '{sentence[:50]}' → {categories}")

    # Step 2: Retrieve + rerank
    rules = retrieve_and_rerank(sentence, categories, top_k_retrieve, top_k_final)

    base = {
        "sentence": sentence,
        "classified_categories": categories,
        "classifier_hints": hints,
        "retrieved_rules": [r["rule_id"] for r in rules],
        "top_rule_score": rules[0]["score"] if rules else 0.0,
    }

    if not use_llm:
        # Return rule metadata only
        if rules:
            top = rules[0]
            return {**base, **{
                "compliant": top["score"] < 0.5,
                "rule_id": top["rule_id"],
                "violation": top["category"],
                "explanation": top["message"],
                "suggestion": top["suggestion"],
                "severity": top["severity"],
                "method": "retrieval_only",
            }}
        return {**base, **{
            "compliant": True,
            "rule_id": None,
            "violation": None,
            "explanation": "No relevant rules retrieved.",
            "suggestion": sentence,
            "severity": "ok",
            "method": "retrieval_only",
        }}

    # Step 3: LLM evaluation
    prompt = _build_review_prompt(sentence, rules)
    raw_response, backend = _call_llm(prompt)

    if raw_response:
        result = _parse_llm_response(raw_response, sentence, rules)
        # Track which backend was used
        result["method"] = f"rag_{backend}"
        result["backend"] = backend
        if backend == "gemini":
            result["privacy_note"] = "sentence sent to Google Gemini API"
        elif backend == "ollama":
            result["privacy_note"] = "processed locally via Ollama (private)"
    elif rules:
        # Gemini unavailable — use top retrieved rule as heuristic
        top = rules[0]
        result = {
            "compliant": top["score"] < 0.45,
            "rule_id": top["rule_id"] if top["score"] >= 0.45 else None,
            "violation": top["category"] if top["score"] >= 0.45 else None,
            "explanation": top["message"] if top["score"] >= 0.45 else "No issues detected.",
            "suggestion": top["example_correction"] if top["score"] >= 0.45 else sentence,
            "severity": top["severity"] if top["score"] >= 0.45 else "ok",
            "method": "rag_heuristic_no_llm",
        }
    else:
        result = {
            "compliant": True,
            "rule_id": None,
            "violation": None,
            "explanation": "No rules matched and LLM unavailable.",
            "suggestion": sentence,
            "severity": "ok",
            "method": "no_data",
        }

    return {**base, **result}


def review_document_sentences(
    sentences: List[str],
    use_llm: bool = True,
    skip_short: int = 8,
) -> List[Dict[str, Any]]:
    """
    Review a list of sentences extracted from a document.

    Args:
        sentences:   List of sentence strings.
        use_llm:     Whether to call Gemini for each sentence.
        skip_short:  Skip sentences with fewer words than this.

    Returns:
        List of feedback dicts, one per (non-skipped) sentence.
    """
    results = []
    for sent in sentences:
        words = sent.strip().split()
        if len(words) < skip_short:
            continue
        feedback = review_sentence(sent, use_llm=use_llm)
        results.append(feedback)
    return results
