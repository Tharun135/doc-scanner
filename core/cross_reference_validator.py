"""
Cross-Reference Validator — Layer 1
Rule IDs: XR-001 through XR-005. Deterministic. No LLM.

Scans the entire DocumentModel for reference integrity violations:
broken internal links, undefined abbreviations, unresolved "see section"
pointers, and missing figures/tables.
"""
from __future__ import annotations
import re
import logging
from dataclasses import dataclass
from typing import List, Optional
from core.document_parser import DocumentModel

logger = logging.getLogger(__name__)

@dataclass
class XRIssue:
    rule_id: str
    severity: str
    message: str
    context: str = ""           # snippet where issue was found
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    suggestion: Optional[str] = None

# Patterns
_SEE_SECTION = re.compile(
    r'\b(?:see|refer to|refer|as described in|described in)\s+'
    r'(?:the\s+)?["\u201c\u201d]?([A-Za-z][A-Za-z0-9 \-/]{2,60})["\u201c\u201d]?\s*'
    r'(?:section|chapter|topic|guide)?',
    re.IGNORECASE,
)
_FIGURE_REF = re.compile(r'\bfigure\s+(\d+)\b', re.IGNORECASE)
_TABLE_REF  = re.compile(r'\btable\s+(\d+)\b',  re.IGNORECASE)
_ABBREV_USE = re.compile(r'\b([A-Z]{2,8}(?:\s[A-Z]{2,8})*)\b')
# Broken reference patterns: (see ...) or [See ...]
_BRACKET_REF = re.compile(r'[\[\(][Ss]ee\s+([^\]\)]{3,60})[\]\)]')

# How many times a term must appear before flagging as "used but undefined"
_UNDEFINED_TERM_THRESHOLD = 3


def validate_cross_references(model: DocumentModel) -> List[XRIssue]:
    """Run all XR checks. Returns a flat list of XRIssues."""
    issues: List[XRIssue] = []
    issues.extend(_check_undefined_abbreviations(model))
    issues.extend(_check_broken_see_references(model))
    issues.extend(_check_missing_figures(model))
    issues.extend(_check_missing_tables(model))
    issues.extend(_check_undefined_terms(model))
    logger.info(f"CrossReferenceValidator: {len(issues)} issues found")
    return issues


def _check_undefined_abbreviations(model: DocumentModel) -> List[XRIssue]:
    """
    XR-002: Abbreviation used before its first expansion.

    For each abbreviation seen in the document, check if it was first
    expanded before (or in the same section as) its earliest use.
    """
    issues: List[XRIssue] = []
    # Build: abbr → index of section where first USED
    abbr_first_use: dict[str, tuple[int, str]] = {}   # abbr → (sec_index, sec_id)
    for idx, sec in enumerate(model.sections):
        for match in _ABBREV_USE.finditer(sec.raw_text):
            abbr = match.group(1)
            if abbr not in abbr_first_use:
                abbr_first_use[abbr] = (idx, sec.id)

    # Build: abbr → index of section where DEFINED
    abbr_defined: dict[str, int] = {}  # abbr → sec_index
    for abbr, (expansion, sec_id) in model.abbreviations.items():
        for idx, sec in enumerate(model.sections):
            if sec.id == sec_id:
                abbr_defined[abbr] = idx
                break

    for abbr, (use_idx, use_sec_id) in abbr_first_use.items():
        if abbr not in model.abbreviations:
            # Only flag common-looking abbreviations (not proper names / single words)
            if len(abbr) >= 2 and ' ' not in abbr and abbr.upper() == abbr:
                sec = model.section_index.get(use_sec_id)
                issues.append(XRIssue(
                    rule_id="XR-002",
                    severity="minor",
                    message=f'Abbreviation "{abbr}" is used but never expanded in the document.',
                    context=f'First seen in section: "{sec.title if sec else use_sec_id}"',
                    section_id=use_sec_id,
                    section_title=sec.title if sec else None,
                    suggestion=f'Add the full form on first use: "Full Name ({abbr})".',
                ))
        elif abbr_defined.get(abbr, 999) > use_idx:
            sec = model.section_index.get(use_sec_id)
            issues.append(XRIssue(
                rule_id="XR-002",
                severity="minor",
                message=f'"{abbr}" is used before it is expanded for the first time.',
                context=f'First used in "{sec.title if sec else use_sec_id}", defined later.',
                section_id=use_sec_id,
                section_title=sec.title if sec else None,
                suggestion='Move the expansion to the first occurrence or add it to a glossary.',
            ))
    return issues


def _check_broken_see_references(model: DocumentModel) -> List[XRIssue]:
    """
    XR-003: "See [section name]" patterns that do not resolve to a known section.
    """
    issues: List[XRIssue] = []
    norm_titles = {t.lower().strip() for t in model.title_index}

    for sec in model.sections:
        for pattern in (_SEE_SECTION, _BRACKET_REF):
            for match in pattern.finditer(sec.raw_text):
                ref_text = match.group(1).strip().lower()
                # Try exact and fuzzy match
                if ref_text not in norm_titles and not _fuzzy_title_match(ref_text, norm_titles):
                    snippet = match.group(0)[:80]
                    issues.append(XRIssue(
                        rule_id="XR-003",
                        severity="major",
                        message=f'Internal reference "{match.group(1).strip()}" does not resolve to any section in this document.',
                        context=f'Found in "{sec.title}": …{snippet}…',
                        section_id=sec.id,
                        section_title=sec.title,
                        suggestion='Verify the section title matches exactly, or update the reference.',
                    ))
    return issues


def _check_missing_figures(model: DocumentModel) -> List[XRIssue]:
    """XR-004: "Figure N" referenced but document appears to contain no figures."""
    issues: List[XRIssue] = []
    all_text = " ".join(s.raw_text for s in model.sections)
    refs = _FIGURE_REF.findall(all_text)
    if not refs:
        return []
    # Simple heuristic: if <img> tags or "Figure" captions exist we consider them defined
    has_figure_captions = bool(re.search(r'\bfigure\s*\d+\s*[:\-–]', all_text, re.IGNORECASE))
    if not has_figure_captions:
        for num in sorted(set(refs)):
            issues.append(XRIssue(
                rule_id="XR-004",
                severity="minor",
                message=f'"Figure {num}" is referenced but no figure caption was found in the document.',
                suggestion='Add a caption "Figure N: Description" near the referenced image.',
            ))
    return issues


def _check_missing_tables(model: DocumentModel) -> List[XRIssue]:
    """XR-004: "Table N" referenced but no table captions found."""
    issues: List[XRIssue] = []
    all_text = " ".join(s.raw_text for s in model.sections)
    refs = _TABLE_REF.findall(all_text)
    if not refs:
        return []
    has_table_captions = bool(re.search(r'\btable\s*\d+\s*[:\-–]', all_text, re.IGNORECASE))
    if not has_table_captions:
        for num in sorted(set(refs)):
            issues.append(XRIssue(
                rule_id="XR-004",
                severity="minor",
                message=f'"Table {num}" is referenced but no table caption was found.',
                suggestion='Add a caption "Table N: Description" above the referenced table.',
            ))
    return issues


def _check_undefined_terms(model: DocumentModel) -> List[XRIssue]:
    """
    XR-001: A term appears many times but is never defined.

    Uses a simple heuristic: if a multi-word phrase (title-cased, 2-4 words)
    appears >= threshold times but has no definition pattern near it, flag it.
    """
    issues: List[XRIssue] = []
    all_text = " ".join(s.raw_text for s in model.sections)

    # Find candidate terms: Title-cased multi-word phrases
    candidates = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', all_text)
    freq: dict[str, int] = {}
    for c in candidates:
        freq[c] = freq.get(c, 0) + 1

    # Definition patterns: "X is a", "X refers to", "X means", "what is X"
    _def_pattern = re.compile(
        r'(?:' + '|'.join(re.escape(t) for t in freq if freq[t] >= _UNDEFINED_TERM_THRESHOLD) + r')'
        r'\s+(?:is|are|means|refers to|describes)',
        re.IGNORECASE,
    ) if any(freq[t] >= _UNDEFINED_TERM_THRESHOLD for t in freq) else None

    for term, count in freq.items():
        if count >= _UNDEFINED_TERM_THRESHOLD:
            if _def_pattern and _def_pattern.search(all_text):
                continue  # term is defined somewhere
            # Skip if it looks like a product name / proper noun already tracked
            if term.lower() in (s.title.lower() for s in model.sections):
                continue
            issues.append(XRIssue(
                rule_id="XR-001",
                severity="minor",
                message=f'"{term}" appears {count} times but is never defined or explained.',
                suggestion=f'Add a definition for "{term}" on first use or in a glossary.',
            ))

    return issues


def _fuzzy_title_match(ref: str, titles: set) -> bool:
    """Return True if ref is a near-match (substring) of any known title."""
    ref_words = set(ref.split())
    for title in titles:
        title_words = set(title.split())
        if ref_words and ref_words.issubset(title_words):
            return True
    return False
