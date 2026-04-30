import requests
import re
import hashlib
import time
import logging
from app.rag.query import retrieve_context

import os
logger = logging.getLogger(__name__)

CONFIG = {
    "rag_top_k": int(os.getenv("RAG_TOP_K", 5)),
    "llm_timeout": int(os.getenv("LLM_TIMEOUT", 5)),
    "max_calls": int(os.getenv("MAX_CALLS", 50)),
    "model": os.getenv("LLM_MODEL", "mistral")
}

PROMPT_VERSION = "v2.1"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"

# Connection pooling to prevent socket exhaustion under load
http_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
http_session.mount('http://', adapter)

cache = {}
global_calls = 0

def parse_llm_output(text, issue_type):
    fallback = {
        "issue": issue_type,
        "suggestion": text.strip() if text else "",
        "ai_answer": "No AI suggestion available. Try again.",
        "prompt_version": PROMPT_VERSION
    }
    
    if not text:
        return fallback

    issue_match = re.search(r"Issue:\s*(.*)", text)
    suggestion_match = re.search(r"Suggestion:\s*(.*)", text)

    if not issue_match or not suggestion_match:
        return fallback

    return {
        "issue": issue_match.group(1).strip(),
        "suggestion": suggestion_match.group(1).strip(),
        "prompt_version": PROMPT_VERSION
    }

def extract_actor(sentence):
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(sentence)
        for token in doc:
            if token.lower_ == "by" and token.dep_ == "agent":
                for child in token.children:
                    if child.dep_ == "pobj":
                        return " ".join([t.text for t in child.subtree])
    except Exception:
        pass
    
    # regex fallback
    match = re.search(r'\bby\s+([a-zA-Z\s]+)', sentence, re.IGNORECASE)
    if match:
        actor_candidate = match.group(1).strip()
        # Exclude common false positive adverbial phrases
        if actor_candidate.lower() not in ["default", "design", "accident", "mistake", "now", "then", "tomorrow"]:
            return actor_candidate
    return None

def is_still_passive(text):
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        for token in doc:
            if token.dep_ == "auxpass":
                return True
            if token.dep_ == "agent" and token.lower_ == "by":
                return True
        return False
    except Exception:
        pass
        
    import re
    passive_be = re.search(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', text, re.IGNORECASE)
    passive_by = re.search(r'\bby\s+(?!default\b|design\b|accident\b|mistake\b|now\b|then\b)\w+', text, re.IGNORECASE)
    return bool(passive_be or passive_by)

def call_llm(sentence, issue_type):
    global global_calls
    if global_calls >= CONFIG["max_calls"]:
        logger.warning(f"Rate limit exceeded ({CONFIG['max_calls']}). Skipping AI generation.")
        return {
            "issue": issue_type,
            "suggestion": "Additional suggestions skipped for performance",
            "prompt_version": PROMPT_VERSION
        }

    global_calls += 1
    
    t0 = time.time()
    try:
        # Retrieve context
        t_rag0 = time.time()
        # Ensure we pass the dynamic config (if the function supports it, or it uses the collection natively)
        # Note: query.py has hardcoded n_results=5, but conceptually we configure it here.
        context = retrieve_context(sentence)
        t_rag_total = (time.time() - t_rag0) * 1000

        # --- Confidence Scoring based on Analytics ---
        import json
        import os
        confidence_level = "Medium"
        acceptance_rate = 0.5
        
        analytics_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'feedback_analytics.json')
        if os.path.exists(analytics_file):
            try:
                with open(analytics_file, 'r') as f:
                    stats = json.load(f)
                if issue_type in stats:
                    accepted = stats[issue_type].get("accept", 0)
                    rejected = stats[issue_type].get("reject", 0)
                    total = accepted + rejected
                    if total >= 5: # Require at least 5 signals for confidence
                        acceptance_rate = accepted / total
                        if acceptance_rate > 0.7:
                            confidence_level = "High"
                        elif acceptance_rate < 0.4:
                            confidence_level = "Low"
            except Exception as e:
                logger.error(f"Error reading analytics: {e}")

        # --- Dynamic Prompting by Issue Type ---
        issue_prompts = {
            "passive_voice": "Strictly rewrite the sentence into active voice. Identify the actor and place them before the verb.",
            "long_sentence": "Split this complex sentence into 2-3 shorter, punchy sentences. Focus on clarity.",
            "unclear_sentence": "Simplify the vocabulary. Remove jargon and restructure for a 10th-grade reading level.",
            "complex_words": "Replace complex vocabulary with simpler, everyday equivalents without losing technical accuracy."
        }
        
        if issue_type == "passive_voice":
            actor = extract_actor(sentence)
            if not actor:
                return {
                    "issue": issue_type,
                    "suggestion": "Clarify who performs the action.",
                    "ai_answer": "Actor missing. Cannot automatically convert to active voice.",
                    "confidence": "Low",
                    "prompt_version": PROMPT_VERSION
                }
            
            prompt = f"""You are a strict technical writing editor.

Task:
Convert the sentence into active voice.

Rules:
- Identify the actor explicitly (Actor: {actor})
- Place the actor at the beginning
- Use present tense
- Keep sentence under 20 words if possible
- Also simplify trailing clauses into clear phrases or split into multiple sentences.
- Do not explain anything

Return ONLY the rewritten sentence.

Sentence:
"{sentence}"
"""
        else:
            specific_instruction = issue_prompts.get(issue_type, "Fix the grammar, improve clarity, and ensure a professional tone.")
            prompt = f"""You are an expert technical writing editor.

Rule Focus:
- {specific_instruction}

Reference Context (Style Guidelines):
{context}

Original sentence:
"{sentence}"

Task:
1. Identify the core issue based on the rule focus.
2. Provide a single, direct rewritten sentence.

Output exactly in this format:
Issue: <Brief description>
Suggestion: <Rewritten sentence>
"""

        def do_llm_call(prompt_text):
            t_llm0 = time.time()
            response = http_session.post(OLLAMA_URL, json={
                "model": CONFIG["model"],
                "prompt": prompt_text,
                "stream": False
            }, timeout=CONFIG["llm_timeout"])
            response.raise_for_status()
            raw_text = response.json().get("response", "")
            return raw_text, (time.time() - t_llm0) * 1000

        raw_text, t_llm_total = do_llm_call(prompt)
        parsed = parse_llm_output(raw_text, issue_type)
        
        if issue_type == "passive_voice":
            if is_still_passive(parsed["suggestion"]):
                # Retry once with a stronger instruction
                retry_prompt = prompt + "\n\nCRITICAL: The previous attempt failed. You MUST remove the word 'by' and make the actor the subject of the sentence."
                raw_text, t_llm_total = do_llm_call(retry_prompt)
                parsed = parse_llm_output(raw_text, issue_type)

            # Deterministic fallback if retry also fails
            if is_still_passive(parsed["suggestion"]):
                if actor:
                    parsed["suggestion"] = f"{actor.capitalize()} performs the action."
                    parsed["ai_answer"] = "AI rewrite failed. Provided deterministic fallback."
                    parsed["confidence"] = "Low"
            
            # Re-evaluate confidence
            if is_still_passive(parsed["suggestion"]):
                confidence_level = "Low"
            elif len(parsed["suggestion"].split()) > 25:
                confidence_level = "Medium"
            else:
                confidence_level = "High"

        parsed["confidence"] = confidence_level
        logger.info(f"Observability - LLM latency: {t_llm_total:.2f}ms | Confidence: {confidence_level}")
        
        # Track transformation success rate
        try:
            transformation_stats_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'transformation_analytics.json')
            stats = {}
            if os.path.exists(transformation_stats_file):
                with open(transformation_stats_file, 'r') as f:
                    stats = json.load(f)
            
            if issue_type not in stats:
                stats[issue_type] = {"success": 0, "failed": 0}
            
            if confidence_level in ["High", "Medium"]:
                stats[issue_type]["success"] += 1
            else:
                stats[issue_type]["failed"] += 1
                
            with open(transformation_stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update transformation analytics: {e}")
            
        return parsed

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Ollama RAG (Network/Timeout): {e}")
        parsed = parse_llm_output(None, issue_type)
        parsed["confidence"] = "Low"
        return parsed
    except Exception as e:
        logger.error(f"Error calling Ollama RAG: {e}")
        parsed = parse_llm_output(None, issue_type)
        parsed["confidence"] = "Low"
        return parsed

cache_stats = {"hits": 0, "misses": 0}

def generate_suggestion(sentence, issue_type):
    global cache_stats
    cache_key = hashlib.md5(f"{sentence}-{issue_type}".encode()).hexdigest()
    
    if cache_key in cache:
        cache_stats["hits"] += 1
        total_requests = cache_stats["hits"] + cache_stats["misses"]
        hit_rate = (cache_stats["hits"] / total_requests) * 100
        logger.info(f"Observability - Cache hit: yes | Hit rate: {hit_rate:.1f}%")
        return cache[cache_key]

    cache_stats["misses"] += 1
    result = call_llm(sentence, issue_type)
    if result is not None:
        cache[cache_key] = result
    return result

def reset_rate_limit():
    global global_calls
    global_calls = 0

