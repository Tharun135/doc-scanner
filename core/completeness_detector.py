"""
Completeness Detector — Hybrid Layer 1 + Layer 3
Rule IDs: COMP-001 through COMP-005.

Layer 1 (deterministic): keyword-pattern checks per section/document type.
Layer 3 (LLM): structured reasoning when L1 finds missing elements.
LLM receives structured JSON context — never raw document text.
"""
from __future__ import annotations
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from core.document_parser import DocumentModel, Section

logger = logging.getLogger(__name__)

@dataclass
class CompletenessIssue:
    rule_id: str
    severity: str
    message: str
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    missing_elements: List[str] = field(default_factory=list)
    llm_explanation: Optional[str] = None   # Populated by Layer 3 if available
    suggestion: Optional[str] = None

# ── Layer 1: Element checklists by document type ──────────────────────────

_PROCEDURE_CHECKLIST: Dict[str, re.Pattern] = {
    "prerequisites": re.compile(
        r'\b(prerequisite|before you (begin|start)|you (will )?need|'
        r'requirements?|ensure|make sure|prior to)\b', re.IGNORECASE),
    "numbered steps": re.compile(
        r'(<ol|^\s*\d+\.)', re.IGNORECASE | re.MULTILINE),
    "expected result": re.compile(
        r'\b(result|outcome|you (will|should) (see|verify|have)|'
        r'successfully|should now|is (now )?complete)\b', re.IGNORECASE),
    "warnings for risky operations": re.compile(
        r'\b(warning|caution|important|note)\b.*\b(delete|remove|'
        r'overwrite|reset|format|data loss)\b|\b(delete|remove|overwrite|'
        r'reset|format|data loss)\b', re.IGNORECASE | re.DOTALL),
}

_CONCEPT_CHECKLIST: Dict[str, re.Pattern] = {
    "definition in opening": re.compile(
        r'\b(is a|refers to|means|is defined as|describes|what is)\b', re.IGNORECASE),
    "concrete example": re.compile(
        r'\b(for example|for instance|such as|e\.g\.|consider|imagine)\b', re.IGNORECASE),
    "use case or scenario": re.compile(
        r'\b(use case|scenario|when to use|applicable when|you can use|'
        r'typical|in practice)\b', re.IGNORECASE),
}

_REFERENCE_CHECKLIST: Dict[str, re.Pattern] = {
    "parameter descriptions": re.compile(
        r'\b(parameter|argument|field|property|attribute|value|type|'
        r'default|required|optional)\b', re.IGNORECASE),
    "data types": re.compile(
        r'\b(string|integer|int|boolean|bool|float|array|list|object|'
        r'json|xml|number|enum)\b', re.IGNORECASE),
}

_CHECKLIST_MAP = {
    "procedure": _PROCEDURE_CHECKLIST,
    "concept": _CONCEPT_CHECKLIST,
    "reference": _REFERENCE_CHECKLIST,
}


def detect_completeness(model: DocumentModel, use_llm: bool = False) -> List[CompletenessIssue]:
    """
    Layer 1 + optional Layer 3 completeness analysis.

    Args:
        model: DocumentModel from parse_document().
        use_llm: If True, call LLM for additional context on Layer 1 findings.
                 LLM receives structured JSON — never raw document text.
    """
    issues: List[CompletenessIssue] = []

    # Document-level completeness
    issues.extend(_document_level_checks(model))

    # Section-level completeness
    for sec in model.sections:
        issues.extend(_section_level_checks(sec, model))

    # Layer 3: LLM enrichment for major issues
    if use_llm and issues:
        major_issues = [i for i in issues if i.severity == "major"]
        for issue in major_issues[:3]:  # Limit LLM calls to top 3
            explanation = _llm_explain_completeness(issue, model)
            if explanation:
                issue.llm_explanation = explanation

    logger.info(f"CompletenessDetector: {len(issues)} issues found")
    return issues


def _document_level_checks(model: DocumentModel) -> List[CompletenessIssue]:
    """Check overall document-level completeness requirements."""
    issues: List[CompletenessIssue] = []
    checklist = _CHECKLIST_MAP.get(model.doc_type)
    if not checklist:
        return []

    all_text = " ".join(s.raw_text for s in model.sections)
    missing = []
    for element, pattern in checklist.items():
        if not pattern.search(all_text):
            missing.append(element)

    if missing:
        issues.append(CompletenessIssue(
            rule_id="COMP-001",
            severity="major",
            message=(
                f'This {model.doc_type} document is missing {len(missing)} '
                f'expected element(s) for its type.'
            ),
            missing_elements=missing,
            suggestion=(
                f'Add the following to complete this {model.doc_type}: '
                f'{", ".join(missing)}.'
            ),
        ))
    return issues


def _section_level_checks(sec: Section, model: DocumentModel) -> List[CompletenessIssue]:
    """Check per-section completeness based on section type signals."""
    issues: List[CompletenessIssue] = []
    if sec.word_count < 30:
        return []

    # Procedure section completeness
    if sec.has_step_content or sec.has_numbered_list:
        checklist = _PROCEDURE_CHECKLIST
        missing = [
            elem for elem, pat in checklist.items()
            if not pat.search(sec.raw_text)
        ]
        if missing:
            # Don't double-report if already caught at document level
            if model.doc_type != "procedure":
                issues.append(CompletenessIssue(
                    rule_id="COMP-002",
                    severity="minor",
                    section_id=sec.id,
                    section_title=sec.title,
                    message=(
                        f'"{sec.title}" appears to be a procedure but is missing: '
                        f'{", ".join(missing)}.'
                    ),
                    missing_elements=missing,
                    suggestion=f'Add {", ".join(missing)} to this section.',
                ))

    # Troubleshooting section completeness
    if re.search(r'\b(error|problem|issue|fail|troubleshoot)\b', sec.title, re.IGNORECASE):
        if not re.search(r'\b(solution|fix|resolve|steps?|workaround|check)\b',
                         sec.raw_text, re.IGNORECASE):
            issues.append(CompletenessIssue(
                rule_id="COMP-003",
                severity="major",
                section_id=sec.id,
                section_title=sec.title,
                message=f'"{sec.title}" describes a problem but provides no solution or resolution steps.',
                missing_elements=["solution or resolution steps"],
                suggestion='Add resolution steps, workarounds, or links to support resources.',
            ))

    # Warning without context
    if re.search(r'\b(warning|caution)\b', sec.raw_text, re.IGNORECASE):
        if not re.search(r'\b(because|since|reason|result|if you|otherwise)\b',
                         sec.raw_text, re.IGNORECASE):
            issues.append(CompletenessIssue(
                rule_id="COMP-004",
                severity="minor",
                section_id=sec.id,
                section_title=sec.title,
                message=f'"{sec.title}" contains a Warning/Caution but does not explain why.',
                missing_elements=["reason or consequence for warning"],
                suggestion='Explain the consequence of ignoring the warning.',
            ))

    return issues


def _llm_explain_completeness(issue: CompletenessIssue, model: DocumentModel) -> Optional[str]:
    """
    Layer 3: Ask LLM to reason about a completeness issue.

    The LLM receives a compact structured context — NOT the raw document.
    Returns the LLM's explanation string, or None on failure.
    """
    try:
        import requests
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_url = f"{ollama_host}/api/generate"
        llm_model = os.getenv("LLM_MODEL", "llama3")

        # Find adjacent sections for context
        sec_titles = [s.title for s in model.sections]
        sec_idx = next(
            (i for i, s in enumerate(model.sections) if s.id == issue.section_id), -1)
        prev_title = sec_titles[sec_idx - 1] if sec_idx > 0 else None
        next_title = sec_titles[sec_idx + 1] if sec_idx < len(sec_titles) - 1 else None

        # Structured context — not raw document text
        context = {
            "section_title": issue.section_title,
            "section_type": model.doc_type,
            "missing_elements": issue.missing_elements,
            "previous_section": prev_title,
            "next_section": next_title,
        }

        prompt = (
            f"You are a technical documentation reviewer.\n\n"
            f"A documentation analysis system found this structured issue:\n"
            f"{json.dumps(context, indent=2)}\n\n"
            f"In 1-2 sentences, explain WHY these missing elements matter for a reader "
            f"and what the impact is if they are absent. Be specific to this section type.\n\n"
            f"Do not repeat the list. Do not suggest rewrites. Just explain the impact."
        )

        resp = requests.post(
            ollama_url,
            json={"model": llm_model, "prompt": prompt, "stream": False},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception as e:
        logger.debug(f"LLM completeness explanation unavailable: {e}")
    return None
