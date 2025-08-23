# scripts/rag_system.py
from typing import List, Dict, Any, Optional
import json
import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "tinyllama:latest"   # you already fallback to this in logs

def _build_present_prompt(feedback_text: str, original_sentence: str, hits: List[Dict[str,Any]]) -> str:
    # compress context for the model; keep it short
    bullets = []
    for h in hits[:3]:
        meta = h.get("metadata", {})
        rule_id = meta.get("rule_id") or meta.get("id") or "unknown"
        sol = (meta.get("solution") or meta.get("solution_text") or h.get("document") or "").strip()
        exp = (meta.get("explanation") or "").strip()
        if sol:
            bullets.append(f"- [{rule_id}] Solution: {sol}\n  Why: {exp}")
    bullets_text = "\n".join(bullets) if bullets else "- (no solution text found)"

    return f"""You are a technical writing assistant.
Issue: {feedback_text}
Original: {original_sentence}

From the solution library (top hits):
{bullets_text}

Write a concise answer in JSON with fields:
- solution_text: short, clear guidance (1–2 sentences).
- proposed_rewrite: rewrite the Original sentence to FIX the issue (active voice and concise).
- sources: array of source rule_ids you used.

Rules:
- Be specific, not generic.
- If the issue is adverb use, remove or relocate weak adverbs.
- If passive voice, convert to active or imperative.
- Do not say "no exact solution".
- Keep output JSON only.
"""

def present_solution(feedback_text: str, original_sentence: str, hits: List[Dict[str,Any]]) -> Dict[str,Any]:
    prompt = _build_present_prompt(feedback_text, original_sentence, hits)
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(OLLAMA_URL, json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You output JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "stream": False
            })
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "")
        # Best-effort JSON parse
        data = json.loads(content)
        # basic shape
        return {
            "solution_text": data.get("solution_text") or "",
            "proposed_rewrite": data.get("proposed_rewrite") or "",
            "sources": data.get("sources") or [h.get("metadata",{}).get("rule_id") for h in hits[:3] if h.get("metadata")]
        }
    except Exception:
        # graceful fallback: stitch from top hit
        top = hits[0] if hits else {}
        meta = top.get("metadata", {})
        return {
            "solution_text": meta.get("solution") or meta.get("solution_text") or "",
            "proposed_rewrite": "",
            "sources": [meta.get("rule_id")] if meta.get("rule_id") else []
        }
