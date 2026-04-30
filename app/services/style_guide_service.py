import requests
import os
import logging
import time
from app.style_guide_context import SIEMENS_STYLE_GUIDE

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TIMEOUT = 15

http_session = requests.Session()

def generate_style_suggestion(sentence, issue_type, feedback_text=""):
    """
    Directly call the LLM with the Siemens Style Guide context to get a rewrite suggestion.
    Skips the RAG pipeline.
    """
    prompt = f"""You are a professional technical editor at Siemens. 
You must rewrite the following sentence according to the official Siemens Style Guide.

### OFFICIAL SIEMENS STYLE GUIDE:
{SIEMENS_STYLE_GUIDE}

### TASK:
- Original Sentence: "{sentence}"
- Detected Issue: {issue_type}
- Feedback: {feedback_text}

### RULES FOR YOUR RESPONSE:
1. Provide a direct, rewritten version of the sentence.
2. Ensure it follows the Style Guide (active voice, present tense, no filler words like 'therefore', use 'must' instead of 'should', etc.).
3. Output exactly in this format:
Issue: <Brief description of the violation>
Suggestion: <The rewritten sentence>

Return ONLY the Issue and Suggestion lines. No explanations.
"""
    
    try:
        start_time = time.time()
        response = http_session.post(OLLAMA_URL, json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=LLM_TIMEOUT)
        
        response.raise_for_status()
        raw_text = response.json().get("response", "").strip()
        latency = (time.time() - start_time) * 1000
        
        logger.info(f"LLM Suggestion generated in {latency:.2f}ms")
        
        # Parse the output
        issue = issue_type
        suggestion = ""
        
        for line in raw_text.split('\n'):
            if line.startswith("Issue:"):
                issue = line.replace("Issue:", "").strip()
            elif line.startswith("Suggestion:"):
                suggestion = line.replace("Suggestion:", "").strip()
        
        # Fallback if parsing fails
        if not suggestion:
            suggestion = raw_text
            
        return {
            "issue": issue,
            "suggestion": suggestion,
            "ai_answer": "Generated via Direct Style Guide LLM Engine",
            "confidence": "high",
            "processing_time": latency
        }
        
    except Exception as e:
        logger.error(f"Error calling LLM for style suggestion: {e}")
        return {
            "issue": issue_type,
            "suggestion": "Could not generate suggestion automatically.",
            "ai_answer": f"Error: {str(e)}",
            "confidence": "low",
            "processing_time": 0
        }

def reset_rate_limit():
    """Compatibility shim for legacy RAG service"""
    pass
