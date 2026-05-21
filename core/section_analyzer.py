"""
Section Analyzer — Layer 1 Rule Engine
Rule IDs: SEC-001 through SEC-007. Deterministic. No LLM.
"""
from __future__ import annotations
import re
import logging
from dataclasses import dataclass
from typing import List, Optional
from core.document_parser import DocumentModel, Section, _WEAK_TITLES

logger = logging.getLogger(__name__)

@dataclass
class SectionIssue:
    rule_id: str
    severity: str          # "major", "minor", "info"
    section_id: str
    section_title: str
    message: str
    reviewer_question: Optional[str] = None
    suggestion: Optional[str] = None

_PREREQ_KW = re.compile(
    r'\b(prerequisite|before you (begin|start)|you (will )?need|requirements?|'
    r'ensure that|make sure|prior to|depends on)\b', re.IGNORECASE)
_OUTCOME_KW = re.compile(
    r'\b(result|outcome|you (will|should|can) (see|verify|check|now)|'
    r'should now|is (now )?complete|successfully|confirm)\b', re.IGNORECASE)
_RISKY_KW = re.compile(
    r'\b(delete|remove|drop|erase|format|overwrite|irreversible|'
    r'cannot be undone|shut down|power off|factory reset|data loss)\b', re.IGNORECASE)
_STEP_KW = re.compile(
    r'(\d+\.\s|\bstep\s+\d|\bfirst\b|\bsecond\b|\bthird\b|\bnext\b|\bthen\b)', re.IGNORECASE)
MAX_WORDS = 800
MIN_WORDS = 20


def analyze_sections(model: DocumentModel) -> List[SectionIssue]:
    """Run all section-level checks. Returns flat list of SectionIssues."""
    issues: List[SectionIssue] = []
    seen: dict[str, str] = {}  # normalized_title → section_id
    for sec in model.sections:
        issues.extend(_empty(sec))
        issues.extend(_procedure(sec, model))
        issues.extend(_warning(sec))
        issues.extend(_duplicate(sec, seen))
        issues.extend(_weak_title(sec))
        issues.extend(_too_long(sec))
        norm = sec.title.lower().strip()
        if norm not in seen:
            seen[norm] = sec.id
    logger.info(f"SectionAnalyzer: {len(issues)} issues across {len(model.sections)} sections")
    return issues


def _empty(sec: Section) -> List[SectionIssue]:
    if sec.word_count < MIN_WORDS:
        return [SectionIssue(
            rule_id="SEC-004", severity="major",
            section_id=sec.id, section_title=sec.title,
            message=f'"{sec.title}" contains only {sec.word_count} word(s). Content appears missing.',
            reviewer_question="Is content missing from this section?",
            suggestion="Add substantive content or merge this section.",
        )]
    return []


def _procedure(sec: Section, model: DocumentModel) -> List[SectionIssue]:
    is_proc = (model.doc_type == "procedure" or sec.has_numbered_list
               or bool(_STEP_KW.search(sec.raw_text)))
    if not is_proc or not sec.has_step_content:
        return []
    issues = []
    parent = model.section_index.get(sec.parent_id or "")
    parent_text = parent.raw_text if parent else ""
    if not _PREREQ_KW.search(sec.raw_text) and not _PREREQ_KW.search(parent_text):
        issues.append(SectionIssue(
            rule_id="SEC-001", severity="major",
            section_id=sec.id, section_title=sec.title,
            message=f'"{sec.title}" has procedural steps but no prerequisite information.',
            reviewer_question="What should the user prepare before starting?",
            suggestion='Add a "Before you begin" subsection.',
        ))
    if not _OUTCOME_KW.search(sec.raw_text):
        issues.append(SectionIssue(
            rule_id="SEC-002", severity="major",
            section_id=sec.id, section_title=sec.title,
            message=f'"{sec.title}" has steps but no expected outcome or verification.',
            reviewer_question="How does the user confirm success?",
            suggestion='Add a "Result" paragraph describing the expected outcome.',
        ))
    return issues


def _warning(sec: Section) -> List[SectionIssue]:
    if not _RISKY_KW.search(sec.raw_text):
        return []
    if re.search(r'\b(warning|caution|danger)\b', sec.raw_text, re.IGNORECASE):
        return []
    return [SectionIssue(
        rule_id="SEC-003", severity="minor",
        section_id=sec.id, section_title=sec.title,
        message=f'"{sec.title}" mentions destructive operations but has no Warning/Caution notice.',
        reviewer_question="Should users be warned before this operation?",
        suggestion='Add a Warning admonition before the risky step.',
    )]


def _duplicate(sec: Section, seen: dict) -> List[SectionIssue]:
    norm = sec.title.lower().strip()
    if norm in seen and seen[norm] != sec.id:
        return [SectionIssue(
            rule_id="SEC-005", severity="major",
            section_id=sec.id, section_title=sec.title,
            message=f'Section title "{sec.title}" appears more than once.',
            reviewer_question="Are these sections covering the same topic?",
            suggestion="Rename, merge, or restructure duplicates.",
        )]
    return []


def _weak_title(sec: Section) -> List[SectionIssue]:
    norm = re.sub(r'[^a-z\s]', '', sec.title.lower()).strip()
    if norm in _WEAK_TITLES:
        return [SectionIssue(
            rule_id="SEC-006", severity="minor",
            section_id=sec.id, section_title=sec.title,
            message=f'Section title "{sec.title}" is too generic.',
            reviewer_question="Can you write a title that describes what this section achieves?",
            suggestion='Use a descriptive title (e.g., "Configuring the network adapter").',
        )]
    return []


def _too_long(sec: Section) -> List[SectionIssue]:
    if sec.word_count > MAX_WORDS:
        return [SectionIssue(
            rule_id="SEC-007", severity="minor",
            section_id=sec.id, section_title=sec.title,
            message=f'"{sec.title}" is {sec.word_count} words — over the {MAX_WORDS}-word limit.',
            reviewer_question="Can this section be divided into subsections?",
            suggestion='Break into H3 subsections to improve scannability.',
        )]
    return []
