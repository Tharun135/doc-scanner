# app/services/enrichment.py
import logging, chromadb, os, re
from functools import lru_cache

logger = logging.getLogger(__name__)
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION = os.getenv("DOCSCANNER_SOLUTIONS_COLLECTION", "docscanner_solutions")

@lru_cache(maxsize=1)
def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        return client.get_collection(COLLECTION)
    except Exception:
        logger.warning("Chroma collection '%s' not found at %s", COLLECTION, CHROMA_PATH)
        return None

def _first_hit_text(hits):
    try:
        return (hits[0]["document"] or "")[:120]
    except Exception:
        return ""

def _best_similarity(hits):
    try:
        return float(hits[0].get("similarity", 0.0))
    except Exception:
        return 0.0

def _create_llm_powered_rewrite(feedback_text: str, sentence_context: str) -> str:
    """Use LLM to create a polished rewrite based on feedback"""
    try:
        # Send direct request to Ollama without going through RAG system
        import requests
        
        # Create a focused prompt for rewriting
        prompt = f"""You are a professional technical writing assistant. Your task is to rewrite the given sentence to fix the specific writing issue.

WRITING ISSUE: {feedback_text}
ORIGINAL SENTENCE: "{sentence_context}"

Instructions:
- Provide ONLY the improved sentence, nothing else
- Fix the specific issue mentioned in the feedback
- Keep the meaning intact
- Make it clear, concise, and professional
- Use active voice when possible
- Follow technical writing best practices

REWRITTEN SENTENCE:"""

        # Send to Ollama using direct API
        ollama_url = "http://localhost:11434/api/generate"
        response = requests.post(ollama_url, json={
            'model': 'phi3:mini',
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,  # Lower temperature for more focused output
                'top_p': 0.9,
                'num_predict': 100   # Limit response length
            }
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            suggestion = result['response'].strip()
            
            # Clean up the response (remove any extra formatting)
            suggestion = suggestion.replace('"', '').strip()
            if suggestion.startswith('REWRITTEN SENTENCE:'):
                suggestion = suggestion[19:].strip()
            if suggestion.startswith('-'):
                suggestion = suggestion[1:].strip()
            if suggestion.startswith('•'):
                suggestion = suggestion[1:].strip()
                
            # Ensure it's different from original and not empty
            if suggestion and suggestion.lower() != sentence_context.lower().strip() and len(suggestion) > 10:
                logger.info(f"LLM generated suggestion: '{suggestion[:100]}...'")
                return suggestion
        else:
            logger.warning(f"Ollama API returned status {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        logger.warning("LLM rewrite failed: Ollama not accessible (connection error)")
    except requests.exceptions.Timeout:
        logger.warning("LLM rewrite failed: Ollama request timed out")
    except Exception as e:
        logger.warning(f"LLM rewrite failed: {e}")
    
    # If LLM fails, return None to trigger deterministic fallback
    return None


def _create_deterministic_rewrite(feedback_text: str, sentence_context: str) -> str:
    """Create a deterministic rewrite based on feedback patterns"""
    import re
    
    text = sentence_context.strip()
    if not text:
        return ""
    
    feedback_lower = feedback_text.lower()
    
    # Passive voice patterns - more comprehensive  
    if "passive voice" in feedback_lower or re.search(r'\b(is|are|was|were)\s+.*\b\w+ed\b', text) or re.search(r'\b(has|have)\s+been\s+\w+', text):
        # Convert passive constructions to active
        text = re.sub(r'\b(is|are)\s+displayed\b', 'appears', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(is|are)\s+shown\b', 'appears', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(is|are)\s+generated\b', 'generates', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(was|were)\s+created\b', 'created', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(is|are)\s+configured\b', 'configures', text, flags=re.IGNORECASE)
        
        # Handle "has/have been + past participle" (present perfect passive)
        text = re.sub(r'\bhas been created\b', 'exists', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave been created\b', 'exist', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhas already been created\b', 'already exists', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave already been created\b', 'already exist', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhas been configured\b', 'is configured', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave been configured\b', 'are configured', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhas been defined\b', 'exists', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave been defined\b', 'exist', text, flags=re.IGNORECASE)
        
        # Handle "are only defined" pattern
        text = re.sub(r'\b(.*?)\s+(are|is)\s+(only\s+)?defined\b', r'The system defines \1 \3', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(.*?)\s+(are|is)\s+(only\s+)?provided\b', r'The system provides \1 \3', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(.*?)\s+(are|is)\s+(only\s+)?supported\b', r'The system supports \1 \3', text, flags=re.IGNORECASE)
        
        # More complex passive patterns
        if 'by the' in text.lower():
            # "X was done by Y" -> "Y does X" pattern
            match = re.search(r'(.*?)\s+(was|were)\s+(\w+ed)\s+by\s+(.*)', text, re.IGNORECASE)
            if match:
                subject, verb, action, actor = match.groups()
                text = f"{actor.strip()} {action.replace('ed', 's')} {subject.strip()}"
        
        # If no specific pattern matched, use imperative for instructions
        if re.search(r'\b(click|select|open|configure|enter|choose)\b', text, re.IGNORECASE):
            text = re.sub(r'^(you can |the user can |the system )', '', text, flags=re.IGNORECASE)
            text = text.capitalize()
        
    # Adverb removal - more comprehensive
    elif "adverb" in feedback_lower or re.search(r'\b(easily|simply|basically|actually|really|generally|typically|optionally)\b', feedback_lower):
        # Remove weak adverbs
        text = re.sub(r'\b(really|easily|simply|basically|actually|generally|typically|optionally)\s+', '', text, flags=re.IGNORECASE)
        # Handle "and optionally" patterns
        text = re.sub(r'\s+and\s+optionally\s+', ' and ', text, flags=re.IGNORECASE)
        text = re.sub(r'\boptionally,?\s*', '', text, flags=re.IGNORECASE)
        
    # Modal verb patterns - more comprehensive
    elif "modal" in feedback_lower or any(word in feedback_lower for word in ["can", "may", "should", "will"]):
        text = re.sub(r'\bclick on\b', 'click', text, flags=re.IGNORECASE)
        text = re.sub(r'\byou may now\b', 'now you can', text, flags=re.IGNORECASE)
        text = re.sub(r'\byou should\b', 'please', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwill be able to\b', 'can', text, flags=re.IGNORECASE)
        
    # Long sentence patterns
    elif "long" in feedback_lower and "sentence" in feedback_lower:
        # Try to break at natural points
        if ', and ' in text:
            parts = text.split(', and ', 1)
            if len(parts) == 2:
                text = f"{parts[0].strip()}. {parts[1].strip().capitalize()}"
        elif ', which ' in text:
            parts = text.split(', which ', 1)
            if len(parts) == 2:
                text = f"{parts[0].strip()}. This {parts[1].strip()}"
    
    # Terminology and consistency
    elif "caps" in feedback_lower or "capital" in feedback_lower or "all caps" in feedback_lower:
        # Fix common capitalization issues
        text = re.sub(r'\bAPI\b', 'API', text)  # Keep API capitalized
        text = re.sub(r'\bURL\b', 'URL', text)  # Keep URL capitalized
        text = re.sub(r'\bCLICK\b', 'Click', text)  # Fix all caps
        text = re.sub(r'\bSELECT\b', 'Select', text)  # Fix all caps
        # Fix ALL CAPS words to sentence case (but preserve acronyms)
        def fix_caps(match):
            word = match.group(0)
            if len(word) <= 3 and word.isupper():  # Likely acronym
                return word
            else:
                return word.capitalize()
        text = re.sub(r'\b[A-Z]{3,}\b', fix_caps, text)
    
    # Clean up spacing and ensure proper sentence structure
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ensure the sentence starts with capital letter and ends with period
    if text and not text[0].isupper():
        text = text[0].upper() + text[1:]
    if text and not text.endswith(('.', '!', '?', ':')):
        text += '.'
    
    # Return improved version, or fallback if no change was made
    if text != sentence_context.strip():
        return text
    else:
        # Fallback: Create a generic but helpful improvement
        if re.search(r'\b(is|are|was|were)\s+\w+ed\b', sentence_context):
            return "Use active voice: " + re.sub(r'\b(is|are|was|were)\s+', '', sentence_context, 1)
        else:
            return f"Improve clarity: {sentence_context.strip()}"

def _policy_rewrite(original: str, policy: dict) -> str:
    """
    Small, deterministic rewriting helpers based on policy metadata.
    Extend as needed (adverbs, passive→active, etc.).
    """
    if not original:
        return ""
    text = original

    # Passive voice nudge (very light heuristic)
    text = re.sub(r"\b(is|are|was|were)\s+([a-z]+ed)\b", r"\2", text, flags=re.IGNORECASE)

    # Adverb overuse (remove common adverbs; policy can supply list)
    if isinstance(policy, dict):
        adverbs = set(map(str.lower, policy.get("adverbs", ["easily", "simply", "basically", "actually"])))
    else:
        adverbs = set(["easily", "simply", "basically", "actually"])
    def drop_adverbs(m):
        word = m.group(0)
        return "" if word.lower() in adverbs else word
    text = re.sub(r"\b\w+ly\b", drop_adverbs, text)

    # Trim multiple spaces
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text

def _force_change(original: str, candidate: str) -> str:
    """Ensure the candidate differs from the original; if not, apply a meaningful improvement."""
    if not candidate:
        return ""
    if original.strip() == candidate.strip():
        # Apply meaningful transformations instead of just adding "(revised)"
        text = original.strip()
        
        # Strategy 1: Convert passive voice to active
        if re.search(r'\b(is|are|was|were)\s+\w+ed\b', text, re.IGNORECASE):
            text = re.sub(r'\b(is|are)\s+(\w+ed)\b', r'appears \2', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(was|were)\s+(\w+ed)\b', r'shows \2', text, flags=re.IGNORECASE)
            if text != original.strip():
                return text
        
        # Strategy 2: Make imperative for UI instructions
        if re.search(r'\b(click|select|open|configure|enter|choose)\b', text, re.IGNORECASE):
            if text.lower().startswith(("you can ", "the user can ")):
                text = re.sub(r'^(you can |the user can )', '', text, flags=re.IGNORECASE)
                text = text.capitalize()
                if text != original.strip():
                    return text
        
        # Strategy 3: Remove unnecessary words
        simplified = re.sub(r'\b(really|easily|simply|basically|actually|generally|typically)\s+', '', text, flags=re.IGNORECASE)
        simplified = re.sub(r'\s+', ' ', simplified).strip()
        if simplified != original.strip() and len(simplified) > 0:
            return simplified
        
        # Strategy 4: Convert "X are displayed" to "X appear" or "The system shows X"
        if 'displayed' in text.lower():
            text = re.sub(r'(.*?)\s+(is|are)\s+displayed', r'The system displays \1', text, flags=re.IGNORECASE)
            if text != original.strip():
                return text
        
        # Strategy 5: Last resort - provide a meaningful generic improvement
        return f"Revise for clarity: {original.strip()}"
    return candidate

def enrich_issue_with_solution(issue: dict) -> dict:
    """
    Input issue:
      {
        "message": "Avoid passive voice...",
        "context": "All the tags configured for the machine will be displayed.",
        "issue_type": "Passive Voice" | "Adverb Overuse" | ...
      }
    Output (mutates and returns the same dict with fields):
      - solution_text (short guidance)
      - proposed_rewrite (concrete sentence)
      - sources (list)
      - method (rag method used)
    """
    
    # FIRST: Try the Ollama RAG system
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'scripts'))
        from ollama_rag_system import get_rag_suggestion
        
        feedback_text = issue.get("message", "")
        sentence_context = issue.get("context", "")
        
        if feedback_text and sentence_context:
            # Get RAG suggestion using the working Ollama system
            rag_result = get_rag_suggestion(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type="general",
                document_content=""
            )
            
            if rag_result and rag_result.get("method") == "ollama_rag_direct":
                # Use the RAG suggestion
                issue["solution_text"] = rag_result.get("suggestion", "").strip()
                
                # Try LLM-powered rewrite first, then deterministic fallback
                llm_rewrite = _create_llm_powered_rewrite(feedback_text, sentence_context)
                issue["proposed_rewrite"] = llm_rewrite or _create_deterministic_rewrite(feedback_text, sentence_context)
                
                issue["sources"] = rag_result.get("sources", [])
                issue["method"] = "rag_rewrite" if llm_rewrite else "rag_fallback"
                
                logger.info("[ENRICH] Using Ollama RAG result: method=%s, suggestion_length=%d", 
                           rag_result.get("method"), len(issue["solution_text"]))
                return issue
                
    except Exception as e:
        logger.warning("[ENRICH] Ollama RAG failed, falling back to ChromaDB: %s", e)
    
    # FALLBACK: Original ChromaDB approach
    col = _get_collection()
    if col is None:
        logger.info("[ENRICH] No Chroma collection available; using LLM-powered fallback.")
        issue["solution_text"] = f"Review and improve this text to address: {issue.get('message', 'writing issue')}"
        
        # Try LLM-powered rewrite first, then deterministic fallback
        llm_rewrite = _create_llm_powered_rewrite(issue.get('message', ''), issue.get('context', ''))
        issue["proposed_rewrite"] = llm_rewrite or _create_deterministic_rewrite(issue.get('message', ''), issue.get('context', ''))
        
        issue["sources"] = []
        issue["method"] = "llm_fallback" if llm_rewrite else "smart_fallback"
        return issue

    query_text = (issue.get("context") or issue.get("message") or "").strip()
    if not query_text:
        logger.info("[ENRICH] Empty query text; bypass.")
        return issue

    # Query vector DB
    try:
        res = col.query(query_texts=[query_text], n_results=4, include=["documents", "metadatas", "distances"])
    except Exception as e:
        logger.error("[ENRICH] Query failed: %s", e, exc_info=True)
        return issue

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    # Normalize hits into a list of dicts with similarity if distances present
    dists = (res.get("distances") or [[]])[0]
    hits = []
    for i, d in enumerate(docs):
        m = metas[i] if i < len(metas) else {}
        sim = 1.0 - float(dists[i]) if i < len(dists) else 0.0
        hits.append({"document": d, "metadata": m, "similarity": sim})

    # Pick best hit
    best = hits[0] if hits else {}
    policy = (best.get("metadata") or {}).get("rewrite_policy", {})  # <== from your enriched JSON
    rule_hint = (best.get("metadata") or {}).get("rule_id", "")

    # Build short guidance
    guidance = (best.get("metadata") or {}).get("solution") or (best.get("metadata") or {}).get("explanation") or ""

    # Compute a proposed rewrite
    original = (issue.get("context") or issue.get("sentence") or "").strip()
    pr = ""
    if policy:
        pr = _policy_rewrite(original, policy)
    # If policy gave nothing good, try extracting from document field (first line, etc.)
    if not pr:
        doc_text = (best.get("document") or "").strip()
        # try a single-line “Proposed:” format if present
        m = re.search(r"(?i)^proposed(?: rewrite)?:\s*(.+)$", doc_text, flags=re.MULTILINE)
        if m:
            pr = m.group(1).strip()

    # Try LLM-powered rewrite first, then use deterministic patterns if needed
    llm_rewrite = _create_llm_powered_rewrite(issue.get("message", ""), original)
    if llm_rewrite:
        pr = llm_rewrite
        method_suffix = "_llm"
    else:
        # Use our improved deterministic rewrite instead of just _force_change
        deterministic_rewrite = _create_deterministic_rewrite(issue.get("message", ""), original)
        if deterministic_rewrite and deterministic_rewrite != original:
            pr = deterministic_rewrite
            method_suffix = "_deterministic"
        else:
            # Last resort: use _force_change only if deterministic patterns failed
            pr = _force_change(original, pr)
            method_suffix = "_fallback"

    # Attach back
    issue["solution_text"] = guidance.strip()
    issue["proposed_rewrite"] = pr.strip()
    issue["sources"] = [{"rule_id": rule_hint, "similarity": round(_best_similarity(hits), 3), "preview": _first_hit_text(hits)}]
    issue["method"] = "chromadb" + method_suffix

    logger.info(
        "[ENRICH] type=%s sim=%.2f rewrite='%s' method=%s",
        issue.get("issue_type"), _best_similarity(hits), issue.get("proposed_rewrite", "")[:120], issue.get("method")
    )
    return issue
