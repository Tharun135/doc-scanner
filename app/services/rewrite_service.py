# app/services/rewrite_service.py
from ollama import chat
import re
from typing import Dict

SYSTEM = (
  "You are a technical-writing rewriter. Apply the provided policy EXACTLY. "
  "Output only the rewritten sentence(s). No explanations. Keep meaning identical."
)

PROMPT_TEMPLATE = """
[ORIGINAL]
{original}

[ISSUE]
{issue_message}

[POLICY]
Voice: {voice}
Mood: {mood}
Tense: {tense}
Templates: {templates}

[FEW-SHOT]
{few_shot}

[EXTRA-HINTS]
{hints}

[CONSTRAINTS]
- Remove UI callouts like: info \"NOTICE\", note \"...\", warning \"...\" if present.
- Do NOT invent details; if the actor is missing, use \"the system\".
- Prefer present tense (declarative) for facts; imperative for steps.
- Keep ≤ 20 words when possible.
"""

_be_forms = r"\\b(am|is|are|was|were|be|been|being)\\b"
_participle = r"[a-z]+ed\\b"
PASSIVE_GUESS = re.compile(fr"{_be_forms}\\s+{_participle}", re.I)
UI_CALLOUT = re.compile(r'^\\s*(info|note|warning|tip)\\s*\".+?\"\\s*', re.I)

def _cleanup_prefix(s: str) -> str:
    return UI_CALLOUT.sub("", s).strip()

def _looks_passive(s: str) -> bool:
    return bool(PASSIVE_GUESS.search(s))

def _format_few_shot(policy: Dict) -> str:
    items = policy.get("few_shot", [])
    return "\\n".join([f"Original: {x.get('original','')}\\nRewrite: {x.get('rewrite','')}" for x in items])

def propose_rewrite(original: str, issue_message: str, policy: Dict) -> str:
    original = _cleanup_prefix(original.strip())
    few = _format_few_shot(policy)
    msg = PROMPT_TEMPLATE.format(
        original=original,
        issue_message=issue_message.strip(),
        voice=policy.get("voice","active"),
        mood=policy.get("mood","declarative"),
        tense=policy.get("tense","present"),
        templates="; ".join(policy.get("templates", [])),
        few_shot=few,
        hints="\\n".join(policy.get("hints", []))
    )
    r = chat(model="llama3", messages=[
        {"role":"system","content": SYSTEM},
        {"role":"user","content": msg}
    ])
    return r["message"]["content"].strip().strip('\"')

def propose_rewrite_strict(original: str, issue_message: str, policy: Dict, max_attempts: int = 2) -> str:
    out = ""
    for _ in range(max_attempts):
        out = propose_rewrite(original, issue_message, policy)
        if not _looks_passive(out):
            break
    return out
