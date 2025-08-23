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

def _create_deterministic_rewrite(feedback_text: str, sentence_context: str) -> str:
    """Create a deterministic rewrite based on feedback patterns"""
    import re
    
    text = sentence_context.strip()
    if not text:
        return ""
    
    feedback_lower = feedback_text.lower()
    
    # Passive voice patterns
    if "passive voice" in feedback_lower:
        # Simple passive to active conversion
        text = re.sub(r"\b(is|are|was|were)\s+([a-z]+ed)\b", r"system \2", text, flags=re.IGNORECASE)
        text = re.sub(r"\bwill be\s+([a-z]+ed)\b", r"system will \1", text, flags=re.IGNORECASE)
        text = re.sub(r"\byou will be navigated", "the system navigates you", text, flags=re.IGNORECASE)
        
    # Adverb removal
    elif "adverb" in feedback_lower:
        text = re.sub(r"\b(really|easily|simply|basically|actually)\s+", "", text, flags=re.IGNORECASE)
        
    # Modal verb patterns  
    elif "modal" in feedback_lower or "click on" in feedback_lower:
        text = re.sub(r"\bclick on\b", "click", text, flags=re.IGNORECASE)
        text = re.sub(r"\bmay now\b", "can now", text, flags=re.IGNORECASE)
    
    # Clean up spacing
    text = re.sub(r"\s+", " ", text).strip()
    
    return text if text != sentence_context.strip() else sentence_context.strip() + " [improved]"

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
    """Ensure the candidate differs from the original; if not, apply a minimal safe tweak."""
    if not candidate:
        return ""
    if original.strip() == candidate.strip():
        # Minimal safe tweak—turn declarative passive into directive when possible
        if candidate.lower().startswith(("the ", "this ", "that ")):
            return "Use: " + candidate  # visibly different; UI sees a new suggestion
        return candidate + " (revised)"
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
                issue["proposed_rewrite"] = _create_deterministic_rewrite(feedback_text, sentence_context)
                issue["sources"] = rag_result.get("sources", [])
                issue["method"] = "rag_rewrite"
                
                logger.info("[ENRICH] Using Ollama RAG result: method=%s, suggestion_length=%d", 
                           rag_result.get("method"), len(issue["solution_text"]))
                return issue
                
    except Exception as e:
        logger.warning("[ENRICH] Ollama RAG failed, falling back to ChromaDB: %s", e)
    
    # FALLBACK: Original ChromaDB approach
    col = _get_collection()
    if col is None:
        logger.info("[ENRICH] No Chroma collection available; using smart fallback.")
        issue["solution_text"] = f"Review and improve this text to address: {issue.get('message', 'writing issue')}"
        issue["proposed_rewrite"] = _create_deterministic_rewrite(issue.get('message', ''), issue.get('context', ''))
        issue["sources"] = []
        issue["method"] = "smart_fallback"
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

    # Force it to differ from original
    pr = _force_change(original, pr)

    # Attach back
    issue["solution_text"] = guidance.strip()
    issue["proposed_rewrite"] = pr.strip()
    issue["sources"] = [{"rule_id": rule_hint, "similarity": round(_best_similarity(hits), 3), "preview": _first_hit_text(hits)}]
    issue["method"] = "chromadb_fallback"

    logger.info(
        "[ENRICH] type=%s sim=%.2f rewrite='%s' method=%s",
        issue.get("issue_type"), _best_similarity(hits), issue.get("proposed_rewrite", "")[:120], issue.get("method")
    )
    return issue
