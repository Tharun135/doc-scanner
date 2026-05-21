"""
Information Architecture Analyzer — Layer 1
Rule IDs: IA-001 through IA-004. Deterministic. No LLM.

Checks the logical ordering and grouping of sections.
"""
from __future__ import annotations
import re
import logging
from dataclasses import dataclass
from typing import List, Optional
from core.document_parser import DocumentModel

logger = logging.getLogger(__name__)

@dataclass
class IAIssue:
    rule_id: str
    severity: str
    message: str
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    suggestion: Optional[str] = None

# Section type classifiers (keyword → type)
_TYPE_KEYWORDS: dict[str, list[str]] = {
    "prerequisites": ["prerequisite", "before you begin", "requirements", "you need"],
    "installation":  ["install", "setup", "set up", "download", "deploy"],
    "configuration": ["configur", "configure", "settings", "set up", "enable", "parameter"],
    "operation":     ["use", "using", "how to", "running", "operate", "workflow"],
    "troubleshooting": ["troubleshoot", "error", "problem", "issue", "fix", "resolve", "fail"],
    "reference":     ["reference", "api", "parameter", "glossary", "appendix", "index"],
    "concepts":      ["what is", "overview", "introduction", "concept", "background", "about"],
}

# Expected high-level ordering of section types
# A section type must NOT appear AFTER a section that should come later
_EXPECTED_ORDER: list[str] = [
    "concepts",
    "prerequisites",
    "installation",
    "configuration",
    "operation",
    "troubleshooting",
    "reference",
]


def analyze_ia(model: DocumentModel) -> List[IAIssue]:
    """Run all IA checks. Returns a flat list of IAIssues."""
    issues: List[IAIssue] = []
    issues.extend(_check_section_ordering(model))
    issues.extend(_check_prerequisites_position(model))
    issues.extend(_check_term_used_before_defined(model))
    issues.extend(_check_mixed_topics(model))
    logger.info(f"IAAnalyzer: {len(issues)} issues found")
    return issues


def _classify_section(sec_title: str, sec_text: str) -> Optional[str]:
    """Return the best-matching section type label, or None."""
    combined = (sec_title + " " + sec_text).lower()
    best_type = None
    best_score = 0
    for stype, keywords in _TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > best_score:
            best_score = score
            best_type = stype
    return best_type if best_score > 0 else None


def _check_section_ordering(model: DocumentModel) -> List[IAIssue]:
    """
    IA-001: Detect sections appearing in illogical order.

    Example: Troubleshooting before Configuration.
    """
    issues: List[IAIssue] = []
    # Only check top-level (level 1 or 2) sections
    top_secs = [s for s in model.sections if s.level <= 2]
    classified = [(s, _classify_section(s.title, s.raw_text)) for s in top_secs]
    classified = [(s, t) for s, t in classified if t is not None]

    for i in range(len(classified)):
        for j in range(i + 1, len(classified)):
            sec_a, type_a = classified[i]
            sec_b, type_b = classified[j]
            if type_a == type_b:
                continue
            idx_a = _EXPECTED_ORDER.index(type_a) if type_a in _EXPECTED_ORDER else -1
            idx_b = _EXPECTED_ORDER.index(type_b) if type_b in _EXPECTED_ORDER else -1
            # sec_b appears BEFORE sec_a in document but AFTER it in expected order
            if idx_a > idx_b and idx_a != -1 and idx_b != -1:
                issues.append(IAIssue(
                    rule_id="IA-001",
                    severity="major",
                    message=(
                        f'Section ordering issue: "{sec_a.title}" ({type_a}) appears '
                        f'after "{sec_b.title}" ({type_b}), but {type_b} content '
                        f'should come before {type_a} content.'
                    ),
                    section_id=sec_a.id,
                    section_title=sec_a.title,
                    suggestion=f'Move "{sec_b.title}" to appear before "{sec_a.title}".',
                ))
    return issues[:5]  # Cap at 5 to avoid over-reporting


def _check_prerequisites_position(model: DocumentModel) -> List[IAIssue]:
    """
    IA-002: Prerequisites section appears after the first procedural step section.

    If a section classified as "prerequisites" appears AFTER any section
    classified as "installation", "configuration", or "operation", that's a problem.
    """
    issues: List[IAIssue] = []
    top_secs = [s for s in model.sections if s.level <= 2]
    classified = [(s, _classify_section(s.title, s.raw_text)) for s in top_secs]

    prereq_positions = [i for i, (_, t) in enumerate(classified) if t == "prerequisites"]
    action_positions = [
        (i, t) for i, (_, t) in enumerate(classified)
        if t in ("installation", "configuration", "operation")
    ]

    for prereq_pos in prereq_positions:
        for action_pos, action_type in action_positions:
            if action_pos < prereq_pos:
                prereq_sec = classified[prereq_pos][0]
                action_sec = classified[action_pos][0]
                issues.append(IAIssue(
                    rule_id="IA-002",
                    severity="major",
                    message=(
                        f'"{prereq_sec.title}" (prerequisites) appears after '
                        f'"{action_sec.title}" ({action_type}). '
                        f'Prerequisites must precede all procedural content.'
                    ),
                    section_id=prereq_sec.id,
                    section_title=prereq_sec.title,
                    suggestion=f'Move "{prereq_sec.title}" to before "{action_sec.title}".',
                ))
    return issues


def _check_term_used_before_defined(model: DocumentModel) -> List[IAIssue]:
    """
    IA-003: A section heading (concept/term) is used in an earlier section
    before the section defining it appears.

    Example: "OPC UA configuration" in step 2, but "Understanding OPC UA" is section 8.
    """
    issues: List[IAIssue] = []
    # Build map: section title words → section index
    title_word_map: dict[str, tuple[int, str]] = {}  # word → (sec_idx, sec_id)
    for idx, sec in enumerate(model.sections):
        # Extract significant words (4+ chars) from heading
        for word in re.findall(r'\b[A-Za-z]{4,}\b', sec.title):
            key = word.lower()
            if key not in title_word_map:
                title_word_map[key] = (idx, sec.id)

    # Now check each section's body for references to later section titles
    for body_idx, sec in enumerate(model.sections):
        body_lower = sec.raw_text.lower()
        for word, (def_idx, def_sec_id) in title_word_map.items():
            if def_idx <= body_idx:
                continue  # Defined before or in this section — OK
            if word not in body_lower:
                continue
            # Skip very common words
            if word in {"introduction", "overview", "section", "chapter", "guide",
                        "document", "following", "previous", "above", "below"}:
                continue
            def_sec = model.section_index.get(def_sec_id)
            issues.append(IAIssue(
                rule_id="IA-003",
                severity="minor",
                message=(
                    f'Term "{word}" is used in "{sec.title}" but is only introduced '
                    f'later in "{def_sec.title if def_sec else def_sec_id}".'
                ),
                section_id=sec.id,
                section_title=sec.title,
                suggestion=(
                    f'Either define "{word}" earlier, or add a forward reference '
                    f'("see {def_sec.title if def_sec else "later section"}").'
                ),
            ))
    return issues[:8]


def _check_mixed_topics(model: DocumentModel) -> List[IAIssue]:
    """
    IA-004: A section contains multiple unrelated topic types.

    Heuristic: if a single section has content matching 3+ distinct topic types,
    it probably covers too many subjects.
    """
    issues: List[IAIssue] = []
    for sec in model.sections:
        if sec.word_count < 100:
            continue
        matched_types = []
        for stype, keywords in _TYPE_KEYWORDS.items():
            combined = (sec.title + " " + sec.raw_text).lower()
            if sum(1 for kw in keywords if kw in combined) >= 2:
                matched_types.append(stype)
        if len(matched_types) >= 3:
            issues.append(IAIssue(
                rule_id="IA-004",
                severity="minor",
                message=(
                    f'"{sec.title}" appears to cover multiple unrelated topics: '
                    f'{", ".join(matched_types)}. '
                    f'Each section should focus on one topic.'
                ),
                section_id=sec.id,
                section_title=sec.title,
                suggestion='Split this section into separate sections, one per topic.',
            ))
    return issues
