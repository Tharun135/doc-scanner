# services/enrichment.py
from typing import List, Dict, Any
from services.solutions_service import get_solution

def enrich_issues_with_rag(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []
    for issue in issues:
        # Expected shape (adjust keys to your actual structure):
        # {
        #   "rule_id": "...",
        #   "issue_type": "Passive Voice",   # if available
        #   "message": "Passive voice: 'The button was clicked'",
        #   "context": "The button was clicked"  # the sentence (if you have it)
        # }
        msg = issue.get("message") or issue.get("detail") or ""
        hint = issue.get("issue_type")
        sol = get_solution(issue_text=msg, issue_type_hint=hint)

        if sol:
            issue["solution_text"] = sol["text"]               # full guidance (includes fix, why, refs)
            issue["solution_meta"] = sol["meta"]               # metadata for UI (explanation, reference)
            issue.setdefault("solution_issue_type", sol["meta"].get("issue_type"))
        else:
            issue["solution_text"] = "No exact solution found in the library."
            issue["solution_meta"] = {"reference": "MSTP / Microsoft Style Guide"}

        enriched.append(issue)
    return enriched
