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

cache = {}
global_calls = 0

def parse_llm_output(text, issue_type):
    fallback = {
        "issue": issue_type,
        "suggestion": text.strip() if text else "No suggestion available (AI unavailable)",
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

        prompt = f"""
You are a strict technical writing reviewer.

Rules:
- Use active voice
- Keep sentences under 20 words
- Use imperative tone for instructions

Context:
{context}

Original sentence:
"{sentence}"

Task:
1. Identify the issue briefly
2. Rewrite the sentence correctly

Output format:
Issue:
Suggestion:
"""

        t_llm0 = time.time()
        response = requests.post(OLLAMA_URL, json={
            "model": CONFIG["model"],
            "prompt": prompt,
            "stream": False
        }, timeout=CONFIG["llm_timeout"])
        
        response.raise_for_status()
        raw_text = response.json().get("response", "")
        t_llm_total = (time.time() - t_llm0) * 1000
        
        parsed = parse_llm_output(raw_text, issue_type)
        logger.info(f"Observability - LLM latency: {t_llm_total:.2f}ms | RAG retrieval time: {t_rag_total:.2f}ms | Cache hit: no")
        return parsed

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Ollama RAG (Network/Timeout): {e}")
        return parse_llm_output(None, issue_type)
    except Exception as e:
        logger.error(f"Error calling Ollama RAG: {e}")
        return parse_llm_output(None, issue_type)

def generate_suggestion(sentence, issue_type):
    cache_key = hashlib.md5(f"{sentence}-{issue_type}".encode()).hexdigest()
    
    if cache_key in cache:
        logger.info("Observability - Cache hit: yes")
        return cache[cache_key]

    result = call_llm(sentence, issue_type)
    if result is not None:
        cache[cache_key] = result
    return result

def reset_rate_limit():
    global global_calls
    global_calls = 0

