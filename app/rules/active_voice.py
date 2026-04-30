"""
Siemens Style Guide — Active Voice Rule (Upgraded)
Rule ID: SG-AV-001

Detects passive voice constructions and flags them per the Siemens IX Style Guide.
This is an upgrade of the original passive_voice rule — it adds section-context
exemptions to eliminate false positives.

Context-aware exemptions:
  - Prerequisites sections: passive is valid (describing a required state, not an action)
  - Notes / Overview / Description / About sections: passive is acceptable
  - Steps / Instructions / Results: passive IS flagged

Replaces: passive_voice.py (the old rule is deduplicated in analyze_sentence via SG-AV-001 normalization)
"""

import re

# ──────────────────────────────────────────────
# Section types that are EXEMPT from passive voice flagging
# ──────────────────────────────────────────────
EXEMPT_BLOCK_TYPES = {"prerequisite", "note", "overview", "description"}

# Heading keywords that signal an exempt section
EXEMPT_HEADING_KEYWORDS = {
    "prerequisite", "prerequisites",
    "requirement", "requirements",
    "system requirement", "system requirements",
    "note", "notes",
    "overview", "about",
    "background", "introduction",
    "what is", "what are",
}

# ──────────────────────────────────────────────
# Passive voice detection patterns
# ──────────────────────────────────────────────

# Common "to be" forms
_BE_FORMS = r"\b(is|are|was|were|be|been|being|has been|have been|had been|will be|would be|can be|could be|should be|must be|may be|might be)\b"

# Past participle pattern: words ending in -ed, plus common irregular past participles
_PAST_PARTICIPLES_IRREGULAR = {
    "written", "done", "made", "given", "taken", "shown", "seen",
    "known", "found", "used", "set", "put", "sent", "built", "brought",
    "bought", "caught", "taught", "thought", "left", "led", "read",
    "run", "begun", "come", "gone", "grown", "drawn", "driven",
    "broken", "chosen", "frozen", "spoken", "stolen", "woven",
    "hidden", "risen", "fallen", "forgiven", "forgotten", "gotten",
    "shaken", "mistaken", "undertaken", "overridden", "withdrawn",
    "opened", "closed", "added", "updated", "configured", "installed",
    "enabled", "disabled", "connected", "imported", "exported",
    "generated", "loaded", "displayed", "highlighted", "flagged",
    "detected", "analyzed", "processed", "executed", "deployed",
    "created", "deleted", "removed", "modified", "changed",
}

# Full passive pattern: be-form + optional adverb + past participle
_PASSIVE_PATTERN = re.compile(
    r"\b(is|are|was|were|be|been|being|has been|have been|had been|"
    r"will be|would be|can be|could be|should be|must be|may be|might be)"
    r"(\s+\w+ly)?\s+"
    r"(\w+ed|" + "|".join(_PAST_PARTICIPLES_IRREGULAR) + r")\b",
    re.IGNORECASE
)

# By-agent pattern: "done by X" — strong signal of passive even without be-form
_BY_AGENT_PATTERN = re.compile(
    r"\b(\w+ed|" + "|".join(_PAST_PARTICIPLES_IRREGULAR) + r")\s+by\b",
    re.IGNORECASE
)

# ──────────────────────────────────────────────
# Known false positive patterns — do not flag
# ──────────────────────────────────────────────
FALSE_POSITIVE_PATTERNS = [
    # "is used to" — valid present usage description (not passive voice error)
    re.compile(r"\bis used to\b", re.IGNORECASE),
    # "is required" in requirement contexts
    re.compile(r"\bis required\b", re.IGNORECASE),
    # "is available" — status description
    re.compile(r"\bis available\b", re.IGNORECASE),
    # "is designed" — product description
    re.compile(r"\bis designed\b", re.IGNORECASE),
    # "is located" — positional reference
    re.compile(r"\bis located\b", re.IGNORECASE),
    # "is shown" in figure references
    re.compile(r"\bis shown in\b", re.IGNORECASE),
]


def _is_exempt_context(heading_context, block_type):
    """
    Return True if the sentence's context exempts it from passive voice flagging.

    A sentence is exempt if:
    - Its block_type is in the exempt set, OR
    - Its heading_context contains an exempt keyword
    """
    # Check block_type first (most reliable — comes from structural parsing)
    if block_type and block_type.lower() in EXEMPT_BLOCK_TYPES:
        return True

    # Check heading keywords
    if heading_context:
        heading_lower = heading_context.lower()
        for keyword in EXEMPT_HEADING_KEYWORDS:
            if keyword in heading_lower:
                return True

    return False


def _is_false_positive(sentence):
    """Return True if the sentence matches a known false positive pattern."""
    for pattern in FALSE_POSITIVE_PATTERNS:
        if pattern.search(sentence):
            return True
    return False


def _build_active_suggestion(match_text, sentence):
    """
    Build a context-appropriate suggestion message.
    We don't rewrite automatically — that requires understanding the actor,
    which is the AI rewriter's job. We provide a clear directive instead.
    """
    return (
        f'Passive voice detected: "{match_text.strip()}". '
        f'Rewrite using active voice and identify who performs the action. '
        f'Example: "The configuration file is opened." → "Click the configuration file to open it."'
    )


def check(sentence, heading_context="", block_type="", tag_name="", **kwargs):
    """
    Check a sentence for passive voice per the Siemens Style Guide.

    Context-aware: suppresses false positives in Prerequisite, Note, Overview,
    Description, and About sections.

    Args:
        sentence (str): The plain text sentence to check.
        heading_context (str): The active heading above this sentence.
        block_type (str): Structural role — step, prerequisite, note, description.
        tag_name (str): HTML tag name — p, li, h1, etc.

    Returns:
        list[dict]: List of issue dicts, or empty list if no violations found.
    """
    if not sentence or not sentence.strip():
        return []

    # ── Context exemption check ────────────────────────────────────────────
    if _is_exempt_context(heading_context, block_type):
        return []

    # ── Skip headings — headings are checked by headings.py ───────────────
    if tag_name and tag_name.lower() in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return []

    # ── False positive filter ──────────────────────────────────────────────
    if _is_false_positive(sentence):
        return []

    issues = []

    # ── Primary: be-form + past participle pattern ─────────────────────────
    for match in _PASSIVE_PATTERN.finditer(sentence):
        match_text = match.group(0)
        issues.append({
            "text": sentence,
            "start": match.start(),
            "end": match.end(),
            "message": _build_active_suggestion(match_text, sentence),
            "suggestion": (
                "Rewrite in active voice. Identify the actor (user, system, application) "
                "and make them the subject of the sentence."
            ),
            "rule_id": "SG-AV-001",
            "category": "active_voice",
            "severity": "warn",
            "color": "yellow",
            "heading_context": heading_context,
            "block_type": block_type,
        })

    # ── Secondary: "done by X" pattern (strong passive signal) ───────────
    if not issues:  # Only check if primary didn't already fire
        for match in _BY_AGENT_PATTERN.finditer(sentence):
            match_text = match.group(0)
            issues.append({
                "text": sentence,
                "start": match.start(),
                "end": match.end(),
                "message": _build_active_suggestion(match_text, sentence),
                "suggestion": (
                    "Move the agent (the doer) to the subject position. "
                    'Example: "done by Admin" → "Admin performs..."'
                ),
                "rule_id": "SG-AV-001",
                "category": "active_voice",
                "severity": "warn",
                "color": "yellow",
                "heading_context": heading_context,
                "block_type": block_type,
            })

    # Return at most one passive voice flag per sentence
    # (multiple pattern matches on the same sentence are the same issue)
    return issues[:1]
