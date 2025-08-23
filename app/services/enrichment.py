# app/services/enrichment.py
from __future__ import annotations
from typing import List
import logging

log = logging.getLogger(__name__)

# --- Prefer the filtered retriever; fall back to robust, then legacy tuple API ---
try:
    # New, quality-gated API you added
    from app.services.solutions_service import retrieve_top_solutions_filtered as _retriever_texts
    _retriever_mode = "filtered"
except Exception:
    try:
        # Older text-only API
        from app.services.solutions_service import retrieve_top_solutions_robust as _retriever_texts
        _retriever_mode = "robust"
    except Exception:
        # Legacy tuple API ([(text, score), ...]) — normalize to texts
        from app.services.solutions_service import retrieve_solution as _retriever_pairs  # type: ignore
        _retriever_mode = "pairs"

def _build_query(feedback: str, context: str) -> str:
    f, c = feedback.strip(), context.strip()
    if not f and not c:
        return ""
    return f"{f}\n\nContext:\n{c}".strip()

def _normalize_results(results) -> List[str]:
    """Normalize any retriever output to List[str]."""
    if not results:
        return []
    if isinstance(results, list) and results and isinstance(results[0], tuple):
        # Legacy shape: [(text, score), ...]
        return [t for (t, _s) in results if t]
    # Text-only list
    return [t for t in results if t]

def enrich_issue_with_solution(
    feedback: str,
    context: str,
    top_k: int = 3,
    max_distance: float = 0.6,  # used only by filtered retriever
) -> dict:
    """
    Uses the preferred retriever to fetch rule/snippet candidates for the issue.
    Returns a dict consumed by ai_improvement.generate_contextual_suggestion.
    """
    query = _build_query(feedback, context)
    if not query:
        log.info("RAG retrieval: empty query -> smart_fallback")
        return {"solutions": [], "_force_change": False, "method": "smart_fallback"}

    try:
        if _retriever_mode == "filtered":
            # Uses max_distance for cosine distance gating inside the retriever
            solutions = _retriever_texts(query, top_k=top_k, max_distance=max_distance)  # type: ignore[arg-type]
        elif _retriever_mode == "robust":
            solutions = _retriever_texts(query, top_k=top_k)  # type: ignore[misc]
        else:
            # pairs mode -> normalize to texts
            pairs = _retriever_pairs(query, top_k=top_k)  # type: ignore[misc]
            solutions = _normalize_results(pairs)

        solutions = solutions[:top_k] if solutions else []
        method = "rag_enriched" if solutions else "smart_fallback"

        log.info(
            "RAG retrieval: mode=%s top_k=%s hits=%s method=%s q=%.40r",
            _retriever_mode, top_k, len(solutions), method, query[:40]
        )

        return {
            "solutions": solutions,
            "_force_change": bool(solutions),  # keep your downstream contract
            "method": method,
        }

    except Exception as e:
        log.exception("RAG enrichment error: %s", e)
        return {
            "solutions": [],
            "_force_change": False,
            "method": "smart_fallback",
        }

# Some callers import this symbol; keep it available.
_force_change = False

__all__ = ["enrich_issue_with_solution", "_force_change"]
