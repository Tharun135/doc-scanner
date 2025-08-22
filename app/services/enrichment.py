# app/services/enrichment.py
from typing import Dict, List, Any, Optional
from app.services.solutions_service import retrieve_solution

FALLBACK_META = {"reference": "MSTP / Microsoft Style Guide"}
FALLBACK_TEXT = "No exact solution found in the library."

def _already_enriched(issues: List[Dict[str, Any]]) -> bool:
    return bool(issues and isinstance(issues, list) and isinstance(issues[0], dict) and "solution_text" in issues[0])

def _attach_fallback(issue: Dict[str, Any]) -> Dict[str, Any]:
    issue.setdefault("solution_text", FALLBACK_TEXT)
    issue.setdefault("solution_meta", FALLBACK_META)
    return issue

def enrich_issue_with_solution(issue: Dict[str, Any]) -> Dict[str, Any]:
    msg: str = (issue.get("message") or issue.get("detail") or "").strip()
    hint: Optional[str] = issue.get("issue_type")

    if not msg:
        return _attach_fallback(issue)

    res = retrieve_solution(issue_text=msg, issue_type_hint=hint)
    if not res:
        return _attach_fallback(issue)

    meta = res["meta"]
    issue["solution_text"] = res["text"]
    issue["solution_meta"] = meta
    issue.setdefault("solution_issue_type", meta.get("issue_type"))

    # ---- Generate a concrete rewrite if we have the original sentence ----
    try:
        from app.services.rewrite_service import propose_rewrite_strict
        policy = meta.get("rewrite_policy", {
            "voice": "active",
            "mood": "declarative_or_imperative",
            "tense": "present",
            "templates": ["<agent> <base_verb> <object>."],
            "few_shot": [],
            "hints": []
        })
        original = issue.get("context") or issue.get("sentence") or ""
        if original:
            issue["proposed_rewrite"] = propose_rewrite_strict(
                original=original,
                issue_message=msg,
                policy=policy
            )
    except Exception:
        # If Ollama or the rewrite service isn't available, just skip
        pass

    return issue

def enrich_issues_with_rag(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if _already_enriched(issues):
        return issues
    return [enrich_issue_with_solution(i) for i in issues]
