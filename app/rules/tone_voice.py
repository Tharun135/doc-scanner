"""
Siemens Style Guide — Tone and Voice Rules
Rule IDs: SG-TV-001 through SG-TV-004

Checks for tone and voice violations per the Siemens IX Style Guide.

SG-TV-001  Negative contraction used         can't → cannot / won't → will not
SG-TV-002  Positive contraction used         you'll → you will / we've → we have
SG-TV-003  Gender-specific language          his/her/him/salesman → their/them/salesperson
SG-TV-004  Informal tone / banned openers    "Hey there", "Simply", "Just do X"
"""

import re

# ──────────────────────────────────────────────
# SG-TV-001: Negative contractions to expand
# ──────────────────────────────────────────────
NEGATIVE_CONTRACTIONS = {
    r"\bcan't\b": ("can't", "cannot"),
    r"\bcannot\b": None,  # already correct — skip
    r"\bwon't\b": ("won't", "will not"),
    r"\bdon't\b": ("don't", "do not"),
    r"\bdoesn't\b": ("doesn't", "does not"),
    r"\bdidn't\b": ("didn't", "did not"),
    r"\bisn't\b": ("isn't", "is not"),
    r"\baren't\b": ("aren't", "are not"),
    r"\bwasn't\b": ("wasn't", "was not"),
    r"\bweren't\b": ("weren't", "were not"),
    r"\bshouldn't\b": ("shouldn't", "should not"),
    r"\bwouldn't\b": ("wouldn't", "would not"),
    r"\bcouldn't\b": ("couldn't", "could not"),
    r"\bhasn't\b": ("hasn't", "has not"),
    r"\bhaven't\b": ("haven't", "have not"),
    r"\bhadn't\b": ("hadn't", "had not"),
    r"\bmustn't\b": ("mustn't", "must not"),
    r"\bneedn't\b": ("needn't", "need not"),
    r"\bdaren't\b": ("daren't", "dare not"),
}

# ──────────────────────────────────────────────
# SG-TV-002: Positive contractions to expand
# ──────────────────────────────────────────────
POSITIVE_CONTRACTIONS = {
    r"\byou'll\b": ("you'll", "you will"),
    r"\byou've\b": ("you've", "you have"),
    r"\byou're\b": ("you're", "you are"),
    r"\byou'd\b": ("you'd", "you would"),
    r"\bwe'll\b": ("we'll", "we will"),
    r"\bwe've\b": ("we've", "we have"),
    r"\bwe're\b": ("we're", "we are"),
    r"\bwe'd\b": ("we'd", "we would"),
    r"\bthey'll\b": ("they'll", "they will"),
    r"\bthey've\b": ("they've", "they have"),
    r"\bthey're\b": ("they're", "they are"),
    r"\bthey'd\b": ("they'd", "they would"),
    r"\bit'll\b": ("it'll", "it will"),
    r"\bit's\b": ("it's", "it is"),
    r"\bthat's\b": ("that's", "that is"),
    r"\bthere's\b": ("there's", "there is"),
    r"\bhere's\b": ("here's", "here is"),
    r"\bwhat's\b": ("what's", "what is"),
    r"\bwho's\b": ("who's", "who is"),
}

# ──────────────────────────────────────────────
# SG-TV-003: Gender-specific language
# ──────────────────────────────────────────────
GENDERED_TERMS = {
    r"\bhis\b": ("his", "their"),
    r"\bhers\b": ("hers", "theirs"),
    r"\bhim\b": ("him", "them"),
    r"\bher\b": ("her", "their / them"),
    r"\bhe\b": ("he", "they"),
    r"\bshe\b": ("she", "they"),
    r"\bsalesman\b": ("salesman", "salesperson"),
    r"\bsalesmen\b": ("salesmen", "salespeople"),
    r"\bchairman\b": ("chairman", "chairperson"),
    r"\bworkman\b": ("workman", "worker"),
    r"\bworkmen\b": ("workmen", "workers"),
    r"\bmanpower\b": ("manpower", "workforce"),
    r"\bmankind\b": ("mankind", "humanity"),
}

# ──────────────────────────────────────────────
# SG-TV-004: Informal tone / banned openers
# ──────────────────────────────────────────────
INFORMAL_PATTERNS = {
    r"\bhey there\b": (
        "hey there",
        'Too informal. Use a neutral greeting or remove entirely. Example: "Welcome to this application."'
    ),
    r"\bhey\b": (
        "hey",
        'Too informal for documentation. Remove or replace with a neutral opener.'
    ),
    r"^hi\b": (
        "hi",
        'Too informal. Use "Welcome" or start with the topic directly.'
    ),
    r"\bit's very easy\b": (
        "it's very easy",
        'Too colloquial. Remove — instructions should be clear without qualifying how easy they are.'
    ),
    r"\bit is very easy\b": (
        "it is very easy",
        'Too colloquial. Remove — instructions should be clear without qualifying how easy they are.'
    ),
    r"\bvery easy\b": (
        "very easy",
        'Avoid qualifiers like "very easy". The instruction should speak for itself.'
    ),
    r"\bsuper easy\b": (
        "super easy",
        'Too colloquial. Remove — instructions should be clear without qualifying how easy they are.'
    ),
    r"\bawesome\b": (
        "awesome",
        'Too informal. Use neutral, professional language.'
    ),
    r"\bcool\b": (
        "cool",
        'Too informal. Use neutral, professional language.'
    ),
    r"\bbasically\b": (
        "basically",
        'Filler word. Remove it — the sentence is clearer without it.'
    ),
    r"\bobviously\b": (
        "obviously",
        'Avoid "obviously" — it can alienate readers who do not find the content obvious.'
    ),
    r"\beasy\b": (
        "easy",
        'Avoid "easy" in instructions. The instruction should stand on its own without qualification.'
    ),
}


def _check_contraction_group(sentence, patterns, rule_id, group_label, expand_note):
    """Shared logic for checking contraction groups (SG-TV-001 / SG-TV-002)."""
    issues = []
    sentence_lower = sentence.lower()
    for pattern, value in patterns.items():
        if value is None:
            continue  # Already correct form — skip
        contraction, expansion = value
        for match in re.finditer(pattern, sentence_lower, re.IGNORECASE):
            issues.append({
                "text": sentence,
                "start": match.start(),
                "end": match.end(),
                "message": (
                    f'{group_label}: Use "{expansion}" instead of "{contraction}". '
                    f'{expand_note}'
                ),
                "suggestion": f'Replace "{contraction}" with "{expansion}".',
                "rule_id": rule_id,
                "category": "tone_voice",
                "severity": "warn",
                "color": "yellow",
                "matched_phrase": contraction,
            })
    return issues


def check(sentence, heading_context="", block_type="", tag_name="", **kwargs):
    """
    Check a sentence for tone and voice violations per the Siemens Style Guide.

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

    issues = []
    sentence_lower = sentence.lower()

    # ── SG-TV-001: Negative contractions ──────────────────────────────────
    issues += _check_contraction_group(
        sentence,
        NEGATIVE_CONTRACTIONS,
        rule_id="SG-TV-001",
        group_label="Negative contraction",
        expand_note="Negative contractions can appear too informal per the Siemens Style Guide."
    )

    # ── SG-TV-002: Positive contractions ──────────────────────────────────
    issues += _check_contraction_group(
        sentence,
        POSITIVE_CONTRACTIONS,
        rule_id="SG-TV-002",
        group_label="Positive contraction",
        expand_note='Use expanded forms to avoid sounding too casual. Example: "you will" not "you\'ll".'
    )

    # ── SG-TV-003: Gender-specific language ───────────────────────────────
    for pattern, (gendered, neutral) in GENDERED_TERMS.items():
        for match in re.finditer(pattern, sentence_lower):
            # Extra check: "her" and "his" can be possessives in neutral contexts
            # e.g. "their" already used — but we flag anyway and let reviewer decide
            issues.append({
                "text": sentence,
                "start": match.start(),
                "end": match.end(),
                "message": (
                    f'Gender-specific language: "{gendered}". '
                    f'Use gender-neutral alternative: "{neutral}".'
                ),
                "suggestion": f'Replace "{gendered}" with "{neutral}".',
                "rule_id": "SG-TV-003",
                "category": "tone_voice",
                "severity": "warn",
                "color": "yellow",
                "matched_phrase": gendered,
            })

    # ── SG-TV-004: Informal tone ───────────────────────────────────────────
    for pattern, (label, suggestion_text) in INFORMAL_PATTERNS.items():
        flags = re.IGNORECASE | re.MULTILINE
        for match in re.finditer(pattern, sentence_lower, flags):
            issues.append({
                "text": sentence,
                "start": match.start(),
                "end": match.end(),
                "message": f'Informal language: "{label}". {suggestion_text}',
                "suggestion": suggestion_text,
                "rule_id": "SG-TV-004",
                "category": "tone_voice",
                "severity": "warn",
                "color": "yellow",
                "matched_phrase": label,
            })

    return issues
