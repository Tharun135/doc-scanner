"""
Siemens Style Guide — Heading Format Rules
Rule IDs: SG-HE-001 through SG-HE-003

Checks headings (h1–h4) for compliance with Siemens IX Style Guide conventions.
Only fires when tag_name is a heading element.

SG-HE-001  Heading not in -ing (gerund) form      "Add element" → "Adding element"
SG-HE-002  Heading uses title case                 "Go To Settings" → "Go to settings"
SG-HE-003  Heading too long (> 6 words)
SG-HE-004  H4 or deeper used                       Consider restructuring into a new topic
"""

import re

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
MAX_HEADING_WORDS = 6

# Words that should NOT trigger SG-HE-002 (proper nouns, product names, acronyms)
# These are always capitalized and are not title-case violations.
ALWAYS_CAPITALIZE = {
    "siemens", "javascript", "python", "linux", "windows", "macos",
    "mindsphere", "ios", "android", "api", "rest", "json", "xml",
    "html", "css", "sql", "mqtt", "opc", "ua", "http", "https",
}

# Action verbs commonly used in headings — used to detect non-gerund forms
# Pattern: bare infinitive at start → suggest -ing form
# We check if the first word is a base verb (no -ing suffix)
_COMMON_BASE_VERBS = {
    "add", "create", "delete", "remove", "update", "edit", "configure",
    "install", "deploy", "connect", "import", "export", "manage", "use",
    "set", "define", "run", "start", "stop", "enable", "disable", "check",
    "view", "open", "close", "save", "upload", "download", "send", "receive",
    "build", "test", "debug", "fix", "change", "move", "copy", "rename",
    "read", "write", "get", "put", "post", "apply", "reset", "restore",
    "access", "navigate", "select", "filter", "search", "sort", "format",
    "generate", "load", "extend", "integrate", "monitor", "track", "log",
}

# Prepositions and articles that should NOT be capitalized in headings
# (only flagged if mid-sentence, not first word)
LOWERCASE_WORDS = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet",
    "at", "by", "in", "of", "on", "to", "up", "as", "if",
    "into", "onto", "with", "from", "over", "after", "before",
    "between", "through", "during", "without",
}


def _is_gerund(word):
    """Return True if word ends in -ing."""
    return word.lower().endswith("ing")


def _to_gerund(word):
    """
    Attempt to convert a base verb to gerund (-ing) form.
    Handles common patterns: double consonant (run→running), drop-e (use→using).
    """
    w = word.lower()
    if w.endswith("e") and len(w) > 2:
        return w[:-1] + "ing"
    # Double final consonant for short CVC words (run, set, get...)
    if len(w) >= 3 and w[-1] not in "aeiou" and w[-2] in "aeiou" and w[-3] not in "aeiou":
        return w + w[-1] + "ing"
    return w + "ing"


def _has_title_case_violation(words):
    """
    Returns a list of (index, word) tuples for words that violate casing rules.
    Rules:
      - First word: always capitalized → no violation
      - Proper nouns / all-caps acronyms: always capitalized → no violation
      - Lowercase function words (prepositions, articles): should NOT be capitalized
      - All other mid-sentence words: should be lowercase
    """
    violations = []
    for i, word in enumerate(words):
        if i == 0:
            continue  # First word is always capitalized — no issue
        clean = re.sub(r"[^a-zA-Z]", "", word)
        if not clean:
            continue
        lower = clean.lower()
        if lower in ALWAYS_CAPITALIZE:
            continue  # Proper noun / product name — ok
        if clean == clean.upper() and len(clean) > 1:
            continue  # All-caps acronym — ok
        # If mid-sentence word starts with uppercase and is not a proper noun
        if clean[0].isupper():
            violations.append((i, word))
    return violations


def check(sentence, heading_context="", block_type="", tag_name="", **kwargs):
    """
    Check headings for Siemens Style Guide compliance.

    Only fires when tag_name is h1–h6. Skips non-heading elements entirely.

    Args:
        sentence (str): The plain text heading text.
        heading_context (str): The active heading above this sentence.
        block_type (str): Structural role.
        tag_name (str): HTML tag name — must be h1–h6 to trigger this rule.

    Returns:
        list[dict]: List of issue dicts, or empty list.
    """
    if not sentence or not sentence.strip():
        return []

    # Only applies to heading elements
    if tag_name.lower() not in HEADING_TAGS:
        return []

    issues = []
    text = sentence.strip()
    words = text.split()

    if not words:
        return []

    first_word = words[0]
    first_word_clean = re.sub(r"[^a-zA-Z]", "", first_word).lower()

    # ── SG-HE-001: Heading not in -ing (gerund) form ──────────────────────
    # Only fires when first word is a known base verb without -ing
    if first_word_clean in _COMMON_BASE_VERBS and not _is_gerund(first_word_clean):
        gerund = _to_gerund(first_word_clean)
        # Reconstruct heading with gerund form
        suggested_heading = gerund.capitalize() + " " + " ".join(words[1:])
        issues.append({
            "text": sentence,
            "start": 0,
            "end": len(sentence),
            "message": (
                f'Use the -ing form for headings: "{text}" → "{suggested_heading}". '
                f'Gerund headings provide a concrete description of the workflow.'
            ),
            "suggestion": suggested_heading,
            "rule_id": "SG-HE-001",
            "category": "headings",
            "severity": "warn",
            "color": "yellow",
        })

    # ── SG-HE-002: Title case violation ───────────────────────────────────
    # All words after the first should be lowercase (except proper nouns/acronyms)
    violations = _has_title_case_violation(words)
    if violations:
        # Build suggested corrected heading
        corrected_words = list(words)
        for idx, word in violations:
            clean = re.sub(r"[^a-zA-Z]", "", word)
            # Lowercase the word, preserve any trailing punctuation
            suffix = word[len(clean):]
            corrected_words[idx] = clean.lower() + suffix

        suggested = " ".join(corrected_words)
        violation_words = [w for _, w in violations]
        issues.append({
            "text": sentence,
            "start": 0,
            "end": len(sentence),
            "message": (
                f'Use lowercase in headings except for the first word and proper nouns. '
                f'Words to lowercase: {", ".join(violation_words)}. '
                f'Suggested: "{suggested}"'
            ),
            "suggestion": suggested,
            "rule_id": "SG-HE-002",
            "category": "headings",
            "severity": "warn",
            "color": "yellow",
        })

    # ── SG-HE-003: Heading too long ───────────────────────────────────────
    if len(words) > MAX_HEADING_WORDS:
        issues.append({
            "text": sentence,
            "start": 0,
            "end": len(sentence),
            "message": (
                f'Heading is {len(words)} words long. Keep headings short and descriptive '
                f'(maximum {MAX_HEADING_WORDS} words). Consider splitting into a shorter '
                f'heading and moving detail into the body text.'
            ),
            "suggestion": f'Shorten to {MAX_HEADING_WORDS} words or fewer.',
            "rule_id": "SG-HE-003",
            "category": "headings",
            "severity": "info",
            "color": "grey",
        })

    # ── SG-HE-004: H4 or deeper ───────────────────────────────────────────
    # "Only levels 2 and 3 are added to the table of contents... use level 4 and below as little as possible"
    try:
        heading_level = int(tag_name[1])  # h4 → 4
        if heading_level >= 4:
            issues.append({
                "text": sentence,
                "start": 0,
                "end": len(sentence),
                "message": (
                    f'Heading level {tag_name.upper()} detected. Only H2 and H3 appear in the '
                    f'table of contents. Consider restructuring this content into a new topic or '
                    f'promoting it to H2/H3 level.'
                ),
                "suggestion": 'Avoid H4 and deeper. Restructure into a new file/topic if the content warrants its own heading.',
                "rule_id": "SG-HE-004",
                "category": "headings",
                "severity": "info",
                "color": "grey",
            })
    except (IndexError, ValueError):
        pass

    return issues
