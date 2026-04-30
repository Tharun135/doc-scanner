"""
Siemens Style Guide — Punctuation and Spacing Rules
Rule IDs: SG-PS-001 through SG-PS-005

Regex-based checks for punctuation and spacing violations defined in the
Siemens IX Style Guide.

SG-PS-001  Space before percent sign        50 % → 50%
SG-PS-002  Missing space before unit        11kg → 11 kg
SG-PS-003  Ampersand in body text           settings & config → settings and config
SG-PS-004  Semicolon in body text           ; used in sentence
SG-PS-005  Brackets used in body text       (see below) → rephrase

Note: SG-PS-005 flags round brackets () only. Square brackets [] used for
cross-references and angle brackets <> for code are excluded.
"""

import re

# ──────────────────────────────────────────────
# Known unit abbreviations (SI and common tech)
# ──────────────────────────────────────────────
UNITS = [
    # SI base
    "kg", "g", "mg", "t",          # mass
    "km", "m", "cm", "mm",         # length
    "l", "ml",                      # volume
    "s", "ms", "us",               # time
    "hz", "khz", "mhz", "ghz",    # frequency
    "w", "kw", "mw",               # power
    "v", "mv", "kv",               # voltage
    "a", "ma",                      # current
    "bits", "bit",                  # data (written out)
    # Storage
    "b", "kb", "mb", "gb", "tb",
    "kib", "mib", "gib", "tib",
    # Misc tech
    "px", "pt", "em", "rem",
    "rpm", "db", "dbm",
]

# Build unit pattern — must follow a digit, unit must be standalone word
_UNIT_PATTERN = re.compile(
    r"(\d)(" + "|".join(UNITS) + r")\b",
    re.IGNORECASE
)

# Known product/company ampersand exceptions — not flagged
_ALLOWED_AMPERSAND_CONTEXTS = [
    "siemens & halske",
    "r&d",
    "q&a",
]


def _has_allowed_ampersand(sentence_lower, match_start):
    """Return True if ampersand sits inside an allowed product/company name."""
    for context in _ALLOWED_AMPERSAND_CONTEXTS:
        idx = sentence_lower.find(context)
        if idx != -1 and idx <= match_start <= idx + len(context):
            return True
    return False


def check(sentence, heading_context="", block_type="", tag_name="", **kwargs):
    """
    Check a sentence for punctuation and spacing violations per the
    Siemens Style Guide.

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

    # ── SG-PS-001: Space before percent sign ──────────────────────────────
    # Bad: "50 %" / "50 %" — Good: "50%"
    for match in re.finditer(r"\d\s+%", sentence):
        issues.append({
            "text": sentence,
            "start": match.start(),
            "end": match.end(),
            "message": 'No space before "%". Write "50%" not "50 %".',
            "suggestion": f'Remove the space: "{match.group().strip()}"',
            "rule_id": "SG-PS-001",
            "category": "punctuation_spacing",
            "severity": "warn",
            "color": "yellow",
        })

    # ── SG-PS-002: Missing space before unit of measurement ───────────────
    # Bad: "11kg", "32bits" — Good: "11 kg", "32 bits"
    # Exception: time expressions like "11am", "4pm" are acceptable
    time_pattern = re.compile(r"\d+(am|pm)\b", re.IGNORECASE)
    time_spans = {m.span() for m in time_pattern.finditer(sentence_lower)}

    for match in _UNIT_PATTERN.finditer(sentence):
        span = match.span()
        # Skip if this overlaps a time expression
        if any(span[0] >= ts[0] and span[1] <= ts[1] for ts in time_spans):
            continue
        digit = match.group(1)
        unit = match.group(2)
        issues.append({
            "text": sentence,
            "start": match.start(),
            "end": match.end(),
            "message": f'Add a space before the unit: "{digit}{unit}" → "{digit} {unit}".',
            "suggestion": f'Write "{digit} {unit}" with a space before the unit.',
            "rule_id": "SG-PS-002",
            "category": "punctuation_spacing",
            "severity": "warn",
            "color": "yellow",
        })

    # ── SG-PS-003: Ampersand in body text ─────────────────────────────────
    # Bad: "Settings & Config" — Good: "Settings and Config"
    # Allowed: "Siemens & Halske AG", "R&D", "Q&A"
    for match in re.finditer(r"&", sentence):
        if not _has_allowed_ampersand(sentence_lower, match.start()):
            issues.append({
                "text": sentence,
                "start": match.start(),
                "end": match.end(),
                "message": 'Avoid "&" in body text. Use "and" instead, unless it is part of a product or company name.',
                "suggestion": 'Replace "&" with "and".',
                "rule_id": "SG-PS-003",
                "category": "punctuation_spacing",
                "severity": "warn",
                "color": "yellow",
            })

    # ── SG-PS-004: Semicolon in body text ─────────────────────────────────
    # Siemens style guide: "Avoid semi-colons."
    for match in re.finditer(r";", sentence):
        issues.append({
            "text": sentence,
            "start": match.start(),
            "end": match.end(),
            "message": 'Avoid semicolons. Split into two sentences or restructure the list.',
            "suggestion": 'Replace the semicolon with a full stop and start a new sentence, or use a bulleted list.',
            "rule_id": "SG-PS-004",
            "category": "punctuation_spacing",
            "severity": "warn",
            "color": "yellow",
        })

    # ── SG-PS-005: Brackets (parentheses) in body text ────────────────────
    # Siemens style guide: "Avoid brackets."
    # Only flag round brackets (). Square [] and angle <> are excluded.
    # Exception: product abbreviation introductions — "SIMATIC PCS (SDC DCA)"
    # are valid on first use. We flag but note the exception in the message.
    for match in re.finditer(r"\([^)]*\)", sentence):
        content = match.group()
        # Heuristic: if bracket content is all caps or short abbreviation → likely a
        # product name introduction, downgrade to info severity
        inner = content[1:-1].strip()
        is_abbreviation = bool(re.match(r"^[A-Z0-9\s\-]{1,20}$", inner))

        if is_abbreviation:
            issues.append({
                "text": sentence,
                "start": match.start(),
                "end": match.end(),
                "message": f'Brackets detected: "{content}". If this is a product abbreviation on first use, this is acceptable. Otherwise, remove brackets and rephrase.',
                "suggestion": 'Only use brackets to introduce a product abbreviation on its first occurrence. Remove brackets elsewhere.',
                "rule_id": "SG-PS-005",
                "category": "punctuation_spacing",
                "severity": "info",
                "color": "grey",
            })
        else:
            issues.append({
                "text": sentence,
                "start": match.start(),
                "end": match.end(),
                "message": f'Avoid brackets: "{content}". Rephrase to integrate the content into the sentence.',
                "suggestion": 'Remove the brackets. Integrate the content into the sentence or move it to a separate sentence.',
                "rule_id": "SG-PS-005",
                "category": "punctuation_spacing",
                "severity": "warn",
                "color": "yellow",
            })

    return issues
