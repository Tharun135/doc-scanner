"""
Consistency Engine — Layer 1
Rule IDs: CON-001 through CON-005. Deterministic. No LLM.

Scans the entire document for consistency violations:
terminology drift, capitalization inconsistency, style drift,
heading style inconsistency, and list type misuse.
"""
from __future__ import annotations
import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from core.document_parser import DocumentModel, Section

logger = logging.getLogger(__name__)

@dataclass
class ConsistencyIssue:
    rule_id: str
    severity: str
    message: str
    examples: List[str] = field(default_factory=list)
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    suggestion: Optional[str] = None

# ── CON-001: Terminology drift ────────────────────────────────────────────
# Groups of synonymous terms that are often used interchangeably
_SYNONYM_GROUPS: List[Tuple[str, ...]] = [
    ("user interface", "ui", "user screen", "dashboard", "frontend", "front end"),
    ("click", "press", "select", "choose", "hit"),
    ("configuration", "config", "settings", "setup", "preferences"),
    ("log in", "login", "sign in", "signin"),
    ("log out", "logout", "sign out", "signout"),
    ("real-time", "real time", "realtime"),
    ("dropdown", "drop-down", "drop down"),
    ("checkbox", "check box", "check-box"),
    ("plugin", "plug-in", "add-on", "addon", "extension"),
    ("username", "user name", "user id", "userid"),
    ("web server", "webserver", "web-server"),
    ("backend", "back end", "back-end"),
    ("ok", "okay", "ok."),
    ("e-mail", "email"),
    ("file name", "filename"),
]

# ── CON-002: Capitalization inconsistency ────────────────────────────────
# Detect the same term written with different capitalizations

# ── CON-003: Active/passive style drift ──────────────────────────────────
_PASSIVE_PATTERN = re.compile(
    r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', re.IGNORECASE)
_ACTIVE_SIGNAL = re.compile(
    r'\b(click|select|enter|configure|run|open|close|enable|disable)\b',
    re.IGNORECASE)

# ── CON-004: Heading style — gerund vs imperative ─────────────────────────
_GERUND_END = re.compile(r'\b\w+ing\b', re.IGNORECASE)
_IMPERATIVE_VERBS = re.compile(
    r'^(Add|Create|Delete|Remove|Update|Edit|Configure|Install|Deploy|Connect|'
    r'Import|Export|Manage|Use|Set|Define|Run|Start|Stop|Enable|Disable|Check|'
    r'View|Open|Close|Save|Upload|Download|Send|Receive|Build|Test|Debug|Fix|'
    r'Change|Move|Copy|Rename|Read|Write|Get|Put|Post|Apply|Reset|Restore|'
    r'Access|Navigate|Select|Filter|Search|Sort|Format|Generate|Load|Extend|'
    r'Integrate|Monitor|Track|Log)\b',
    re.IGNORECASE,
)


def analyze_consistency(model: DocumentModel) -> List[ConsistencyIssue]:
    """Run all consistency checks. Returns flat list of ConsistencyIssues."""
    issues: List[ConsistencyIssue] = []
    issues.extend(_terminology_drift(model))
    issues.extend(_capitalization_drift(model))
    issues.extend(_style_drift(model))
    issues.extend(_heading_style_inconsistency(model))
    issues.extend(_list_type_misuse(model))
    logger.info(f"ConsistencyEngine: {len(issues)} issues found")
    return issues


def _terminology_drift(model: DocumentModel) -> List[ConsistencyIssue]:
    """CON-001: Detect multiple synonymous terms used for the same concept."""
    issues: List[ConsistencyIssue] = []
    all_text = " ".join(s.raw_text.lower() for s in model.sections)

    for group in _SYNONYM_GROUPS:
        found = [term for term in group if re.search(r'\b' + re.escape(term) + r'\b', all_text)]
        if len(found) >= 2:
            issues.append(ConsistencyIssue(
                rule_id="CON-001",
                severity="minor",
                message=(
                    f'Terminology drift detected: the document uses {len(found)} different terms '
                    f'for the same concept.'
                ),
                examples=[f'"{t}"' for t in found],
                suggestion=(
                    f'Choose one term and use it consistently: {found[0]!r}. '
                    f'Replace all other variants throughout the document.'
                ),
            ))
    return issues


def _capitalization_drift(model: DocumentModel) -> List[ConsistencyIssue]:
    """
    CON-002: Detect the same word written with different capitalizations.

    Strategy: collect all title-cased words (>= 3 chars), group by lowercase
    form, flag groups where both Title-cased and lower-cased variants exist.
    """
    issues: List[ConsistencyIssue] = []
    # Map: lowercase → set of observed capitalizations
    cap_map: Dict[str, Set[str]] = {}
    for sec in model.sections:
        for word in re.findall(r'\b[A-Za-z]{3,}\b', sec.raw_text):
            key = word.lower()
            cap_map.setdefault(key, set()).add(word)

    # Flag words that appear both capitalized and lowercased (not just start-of-sentence)
    already_reported: Set[str] = set()
    for key, variants in cap_map.items():
        # Only report if genuinely mixed (not trivial sentence-start cap)
        lc_variants = {v for v in variants if v[0].islower()}
        uc_variants = {v for v in variants if v[0].isupper()}
        if lc_variants and uc_variants and key not in already_reported:
            # Only flag domain-like terms, skip common words
            if len(key) >= 5 and key not in {
                "the", "and", "for", "with", "this", "that", "from",
                "have", "been", "will", "would", "should", "could",
                "their", "they", "there", "then", "when", "what",
                "which", "where", "who", "how", "its", "also",
            }:
                # Limit to 3 examples to avoid noise
                sample = list(lc_variants)[:1] + list(uc_variants)[:2]
                issues.append(ConsistencyIssue(
                    rule_id="CON-002",
                    severity="minor",
                    message=f'"{key}" appears with inconsistent capitalization.',
                    examples=[f'"{v}"' for v in sample],
                    suggestion=f'Decide on one capitalization for "{key}" and apply it throughout.',
                ))
                already_reported.add(key)

    # Cap at 10 to avoid overwhelming the report
    return issues[:10]


def _style_drift(model: DocumentModel) -> List[ConsistencyIssue]:
    """
    CON-003: Active vs passive style drift between sections.

    Flags if some sections are predominantly active and others predominantly passive.
    """
    issues: List[ConsistencyIssue] = []
    section_styles: List[Tuple[str, str, float]] = []  # (sec_id, title, passive_ratio)

    for sec in model.sections:
        if sec.word_count < 50:
            continue
        sentences = [s for s in sec.sentences if len(s.split()) > 5]
        if not sentences:
            continue
        passive_count = sum(1 for s in sentences if _PASSIVE_PATTERN.search(s))
        ratio = passive_count / len(sentences)
        section_styles.append((sec.id, sec.title, ratio))

    if len(section_styles) < 2:
        return []

    # Find sections strongly active vs strongly passive
    active_secs = [s for s in section_styles if s[2] < 0.2]
    passive_secs = [s for s in section_styles if s[2] > 0.6]

    if active_secs and passive_secs:
        examples = (
            [f'"{t}" (active style)' for _, t, _ in active_secs[:2]] +
            [f'"{t}" (passive style)' for _, t, _ in passive_secs[:2]]
        )
        issues.append(ConsistencyIssue(
            rule_id="CON-003",
            severity="minor",
            message=(
                f'Style drift detected: {len(active_secs)} section(s) use predominantly active voice '
                f'while {len(passive_secs)} section(s) use predominantly passive voice.'
            ),
            examples=examples,
            suggestion='Standardize on active voice throughout. Use imperative mood for procedures.',
        ))
    return issues


def _heading_style_inconsistency(model: DocumentModel) -> List[ConsistencyIssue]:
    """
    CON-004: Mix of gerund and imperative headings at the same level.

    Siemens style requires gerund headings ("Configuring", not "Configure").
    Flag when both styles appear at the same heading level.
    """
    issues: List[ConsistencyIssue] = []
    # Group headings by level
    by_level: Dict[int, List[str]] = {}
    for sec in model.sections:
        by_level.setdefault(sec.level, []).append(sec.title)

    for level, titles in by_level.items():
        if len(titles) < 2:
            continue
        gerund = [t for t in titles if _GERUND_END.match(t.split()[0]) if t.split()]
        imperative = [t for t in titles if _IMPERATIVE_VERBS.match(t)]
        # Remove gerunds from imperative list (they can match both)
        imperative = [t for t in imperative if t not in gerund]
        if gerund and imperative:
            issues.append(ConsistencyIssue(
                rule_id="CON-004",
                severity="minor",
                message=(
                    f'H{level} headings mix gerund and imperative forms. '
                    f'Style guide requires gerund form for all headings.'
                ),
                examples=(
                    [f'"{t}" (gerund ✓)' for t in gerund[:2]] +
                    [f'"{t}" (imperative ✗)' for t in imperative[:2]]
                ),
                suggestion='Use gerund form for all headings: "Configuring X" not "Configure X".',
            ))
    return issues


def _list_type_misuse(model: DocumentModel) -> List[ConsistencyIssue]:
    """
    CON-005: Procedure steps described in bullet lists instead of numbered lists.

    Flags sections that have step-like content (imperative sentences with sequence
    language) but use bullet lists (<ul>) instead of numbered lists (<ol>).
    """
    issues: List[ConsistencyIssue] = []
    for sec in model.sections:
        if sec.has_step_content and sec.has_bullet_list and not sec.has_numbered_list:
            if sec.word_count > 50:
                issues.append(ConsistencyIssue(
                    rule_id="CON-005",
                    severity="minor",
                    section_id=sec.id,
                    section_title=sec.title,
                    message=(
                        f'"{sec.title}" contains procedural steps in a bullet list. '
                        f'Procedures must use numbered lists to convey sequence.'
                    ),
                    suggestion='Convert bullet list to a numbered list for this procedure.',
                ))
    return issues
