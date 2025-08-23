# app/services/enrichment.py
from typing import Dict, Any, List, Optional
from .solutions_service import retrieve_top_solutions
from .rewriter import propose_rewrite_strict

# Small defaults as safety nets
DEFAULT_ACTIVE_VOICE_POLICY = { "voice":"active", "mood":"declarative_or_imperative", "tense":"present" }
DEFAULT_ADVERB_POLICY = {
    "goal":"reduce/relocate adverbs",
    "adverbs_to_downtone":["easily","simply","basically","clearly","quickly","actually"]
}

def _pick_policy(issue_msg: str, top_hit_meta: Optional[Dict[str,Any]]) -> Dict[str,Any]:
    # Prefer policy in metadata if present
    if top_hit_meta:
        pol = top_hit_meta.get("rewrite_policy") or top_hit_meta.get("policy")
        if isinstance(pol, dict): return pol
    # Heuristic fallback by issue type
    msg = (issue_msg or "").lower()
    if "adverb" in msg:
        return DEFAULT_ADVERB_POLICY
    return DEFAULT_ACTIVE_VOICE_POLICY

def enrich_issue_with_solution(issue: Dict[str,Any]) -> Dict[str,Any]:
    """
    Enrich an issue with:
    - retrieval hits (top 1-3) from Chroma
    - an LLM-presented solution text
    - a concrete proposed_rewrite tailored to original sentence
    """
    issue = dict(issue)  # shallow copy
    message = issue.get("message", "")
    original = issue.get("context") or issue.get("sentence") or ""
    hint = issue.get("issue_type", "") or ""

    # 1) Retrieve from vector DB
    hits = retrieve_top_solutions(query_text=message, issue_type_hint=hint, top_k=3)
    issue["retrieval_hits"] = hits  # useful for debugging / sources

    # 2) Ask LLM to present a clean solution (if we have hits)
    solution_text = None
    try:
        if hits:
            from scripts.rag_system import present_solution  # you'll add this below
            solution = present_solution(
                feedback_text=message,
                original_sentence=original,
                hits=hits
            )
            # expect: {"solution_text": "...", "proposed_rewrite": "...", "sources":[...]}
            if isinstance(solution, dict):
                solution_text = solution.get("solution_text")
                if solution.get("proposed_rewrite"):
                    issue["proposed_rewrite"] = solution["proposed_rewrite"]
                if solution.get("sources"):
                    issue["sources"] = solution["sources"]
    except Exception:
        pass

    if solution_text:
        issue["solution_text"] = solution_text

    # 3) Ensure we ALWAYS have a proposed_rewrite (policy + deterministic)
    if not issue.get("proposed_rewrite") and original:
        policy = _pick_policy(message, hits[0]["metadata"] if hits else None)
        try:
            rewrite = propose_rewrite_strict(
                original=original,
                issue_message=message,
                policy=policy
            )
            if rewrite and rewrite.strip():
                issue["proposed_rewrite"] = rewrite.strip()
        except Exception:
            # leave as-is; engine will fallback
            pass

    return issue
