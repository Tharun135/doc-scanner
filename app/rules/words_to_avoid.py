"""
Siemens Style Guide — Words and Phrases to Avoid
Rule ID: SG-WA-001

Scans for banned words and phrases defined in the Siemens IX Style Guide.
Runs as a pure dictionary/regex scan — no AI or spaCy required.

Exempt block types: none (words-to-avoid applies document-wide)
"""

import re

# ──────────────────────────────────────────────
# Banned words/phrases — key: pattern, value: (display_label, suggestion)
# ──────────────────────────────────────────────
BANNED_PHRASES = {
    # Filler expressions
    r"\bfor that reason\b": (
        "for that reason",
        'Remove filler expression. State the result directly.'
    ),
    r"\btherefore\b": (
        "therefore",
        'Remove filler word. Restructure the sentence to show causality directly.'
    ),
    r"\baccording\b": (
        "according",
        'Remove filler word. State the source or fact directly.'
    ),
    r"\bfurthermore\b": (
        "furthermore",
        'Remove filler word. Start a new sentence with the new point.'
    ),

    # Too generic
    r"\bto do\b": (
        "to do",
        'Too generic. Replace with a specific action verb, for example: "to configure", "to upload", "to delete".'
    ),

    # Interpretation room
    r"\bshould\b": (
        "should",
        'Provides room for interpretation. Use "must" for requirements or rewrite as a direct instruction.'
    ),
    r"\bcould\b": (
        "could",
        'Provides room for interpretation. Use "can" for capability or rewrite as a direct instruction.'
    ),

    # Inappropriate terminology
    r"\bmaster\b": (
        "master",
        'Not appropriate. Use "primary", "main", or "source" instead.'
    ),
    r"\bslave\b": (
        "slave",
        'Not appropriate. Use "secondary", "replica", or "target" instead.'
    ),

    # Weak expressions
    r"\bit is\b": (
        "it is",
        'Weak expression. Rewrite actively. Example: "It is important to save" → "Save the file before closing."'
    ),
    r"\bthere is\b": (
        "there is",
        'Weak expression. Rewrite actively. Example: "There is a setting" → "A setting controls this behavior."'
    ),
    r"\bthere are\b": (
        "there are",
        'Weak expression. Rewrite actively. Example: "There are three options" → "Three options are available."'
    ),

    # Politeness overuse
    r"\bplease\b": (
        "please",
        'Remove "please" unless apologizing for something inconvenient or unplanned.'
    ),

    # Colloquial
    r"\bsimply\b": (
        "simply",
        'Too colloquial. Remove it — the instruction should speak for itself.'
    ),
    r"\bjust\b": (
        "just",
        'Too colloquial. Remove it — the instruction should speak for itself.'
    ),

    # Abbreviations
    r"\be\.g\.\b": (
        "e.g.",
        'Use "for example" or "such as" instead of "e.g."'
    ),
    r"\be\.\s+g\.\b": (
        "e. g.",
        'Use "for example" or "such as" instead of "e. g."'
    ),

    # Time-based vocabulary misuse
    r"\blast update\b": (
        "last update",
        'Use "latest update" — "last" implies nothing more follows.'
    ),
    r"\blast version\b": (
        "last version",
        'Use "previous version" — "last" implies nothing more follows.'
    ),
    r"\blast events\b": (
        "last events",
        'Use "recent events" — "last" implies nothing more follows.'
    ),
}


def check(sentence, heading_context="", block_type="", tag_name="", **kwargs):
    """
    Check a sentence for banned words and phrases per the Siemens Style Guide.

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

    for pattern, (label, suggestion_text) in BANNED_PHRASES.items():
        matches = list(re.finditer(pattern, sentence_lower))
        for match in matches:
            start = match.start()
            end = match.end()

            # Preserve original casing from the sentence for display
            original_word = sentence[start:end]

            issues.append({
                "text": sentence,
                "start": start,
                "end": end,
                "message": f'Avoid "{label}". {suggestion_text}',
                "suggestion": suggestion_text,
                "rule_id": "SG-WA-001",
                "category": "words_to_avoid",
                "severity": "warn",
                "color": "yellow",
                "matched_phrase": original_word,
            })

    return issues
