"""
Flow Analyzer — Hybrid Layer 1 + Layer 3
Rule IDs: FL-001 through FL-003.

Layer 1 (deterministic): keyword overlap, transition detection.
Layer 3 (LLM): structured reasoning on abrupt section transitions.
"""
from __future__ import annotations
import json
import logging
import os
import re
from dataclasses import dataclass
from typing import List, Optional, Set
from core.document_parser import DocumentModel, Section

logger = logging.getLogger(__name__)

@dataclass
class FlowIssue:
    rule_id: str
    severity: str
    message: str
    section_a_title: Optional[str] = None
    section_b_title: Optional[str] = None
    section_id: Optional[str] = None
    llm_explanation: Optional[str] = None
    suggestion: Optional[str] = None

# Transition language patterns
_TRANSITION_PATTERNS = re.compile(
    r'\b(next|now|following|in the next|as described|in this section|'
    r'this section|after completing|once you have|having configured|'
    r'the following|see also|refer to)\b',
    re.IGNORECASE,
)

# Stop words for keyword overlap computation
_STOP_WORDS: Set[str] = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "that", "this",
    "these", "those", "it", "its", "you", "your", "we", "our", "they",
    "their", "not", "no", "so", "if", "then", "when", "where", "how",
    "all", "any", "each", "more", "also", "which", "who", "there", "here",
}

_MIN_OVERLAP_RATIO = 0.15    # Sections sharing < 15% keywords are flagged as abrupt
_MIN_SECTION_WORDS = 40      # Only check sections with enough content


def analyze_flow(model: DocumentModel, use_llm: bool = False) -> List[FlowIssue]:
    """
    Run all flow checks. Optionally enrich severe findings with LLM reasoning.
    """
    issues: List[FlowIssue] = []
    issues.extend(_check_abrupt_transitions(model))
    issues.extend(_check_missing_transition_sentences(model))
    issues.extend(_check_orphaned_sections(model))

    if use_llm:
        for issue in issues[:3]:
            if issue.severity == "major" and issue.llm_explanation is None:
                issue.llm_explanation = _llm_explain_transition(issue, model)

    logger.info(f"FlowAnalyzer: {len(issues)} flow issues found")
    return issues


def _keywords(text: str) -> Set[str]:
    """Extract significant keywords from text (no stop words, >= 4 chars)."""
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    return {w for w in words if w not in _STOP_WORDS}


def _overlap_ratio(kw_a: Set[str], kw_b: Set[str]) -> float:
    """Jaccard-like overlap ratio between two keyword sets."""
    if not kw_a or not kw_b:
        return 0.0
    intersection = kw_a & kw_b
    union = kw_a | kw_b
    return len(intersection) / len(union)


def _check_abrupt_transitions(model: DocumentModel) -> List[FlowIssue]:
    """
    FL-001: Consecutive sections with very low keyword overlap (< threshold).

    Indicates a likely abrupt topic jump.
    Only checks top-level (H1/H2) sections.
    """
    issues: List[FlowIssue] = []
    top_secs = [s for s in model.sections
                if s.level <= 2 and s.word_count >= _MIN_SECTION_WORDS]

    for i in range(len(top_secs) - 1):
        sec_a = top_secs[i]
        sec_b = top_secs[i + 1]
        kw_a = _keywords(sec_a.raw_text + " " + sec_a.title)
        kw_b = _keywords(sec_b.raw_text + " " + sec_b.title)
        ratio = _overlap_ratio(kw_a, kw_b)

        if ratio < _MIN_OVERLAP_RATIO:
            issues.append(FlowIssue(
                rule_id="FL-001",
                severity="minor",
                message=(
                    f'Abrupt transition detected between "{sec_a.title}" and '
                    f'"{sec_b.title}". These sections share very few common concepts '
                    f'({ratio:.0%} keyword overlap).'
                ),
                section_a_title=sec_a.title,
                section_b_title=sec_b.title,
                section_id=sec_b.id,
                suggestion=(
                    f'Add a bridging sentence at the end of "{sec_a.title}" that '
                    f'previews "{sec_b.title}", or add a transition heading.'
                ),
            ))
    return issues


def _check_missing_transition_sentences(model: DocumentModel) -> List[FlowIssue]:
    """
    FL-002: Section ends without a transition sentence.

    A transition sentence typically contains words like "next", "now",
    "see also", "following", etc.
    Only applies to procedural sections with step content.
    """
    issues: List[FlowIssue] = []
    top_secs = [s for s in model.sections
                if s.level <= 2 and s.word_count >= _MIN_SECTION_WORDS]

    for i, sec in enumerate(top_secs[:-1]):  # Skip last section
        if not sec.has_step_content:
            continue
        last_sentence = sec.sentences[-1] if sec.sentences else ""
        if not _TRANSITION_PATTERNS.search(last_sentence):
            next_sec = top_secs[i + 1]
            issues.append(FlowIssue(
                rule_id="FL-002",
                severity="info",
                message=(
                    f'"{sec.title}" ends without a transition to the next section. '
                    f'Readers may not know what to do after completing this section.'
                ),
                section_a_title=sec.title,
                section_b_title=next_sec.title,
                section_id=sec.id,
                suggestion=(
                    f'Add a closing sentence such as: '
                    f'"After completing this step, proceed to {next_sec.title}."'
                ),
            ))
    return issues


def _check_orphaned_sections(model: DocumentModel) -> List[FlowIssue]:
    """
    FL-003: A section's topic is not referenced by any adjacent section.

    Heuristic: If a top-level section's title keywords don't appear at all
    in the surrounding sections, it may be contextually isolated.
    """
    issues: List[FlowIssue] = []
    top_secs = [s for s in model.sections if s.level <= 2]

    for i, sec in enumerate(top_secs):
        if sec.word_count < _MIN_SECTION_WORDS:
            continue
        title_kw = _keywords(sec.title)
        if not title_kw:
            continue

        # Check if title keywords appear in immediate neighbours
        neighbour_texts = []
        if i > 0:
            neighbour_texts.append(top_secs[i - 1].raw_text.lower())
        if i < len(top_secs) - 1:
            neighbour_texts.append(top_secs[i + 1].raw_text.lower())

        if not neighbour_texts:
            continue

        combined_neighbours = " ".join(neighbour_texts)
        referenced = any(kw in combined_neighbours for kw in title_kw)

        if not referenced and len(title_kw) >= 2:
            issues.append(FlowIssue(
                rule_id="FL-003",
                severity="info",
                message=(
                    f'"{sec.title}" appears disconnected from adjacent sections. '
                    f'Its topic is not referenced by surrounding content.'
                ),
                section_id=sec.id,
                section_a_title=sec.title,
                suggestion=(
                    'Consider adding cross-references or transition sentences that '
                    'connect this section to the surrounding content.'
                ),
            ))
    return issues


def _llm_explain_transition(issue: FlowIssue, model: DocumentModel) -> Optional[str]:
    """
    Layer 3: Ask LLM to reason about an abrupt transition.

    Sends compact structured context — never raw document text.
    """
    try:
        import requests
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_url = f"{ollama_host}/api/generate"
        llm_model = os.getenv("LLM_MODEL", "llama3")

        # Build structured context from section metadata only
        sec_a = next((s for s in model.sections if s.title == issue.section_a_title), None)
        sec_b = next((s for s in model.sections if s.title == issue.section_b_title), None)

        context = {
            "section_a": {
                "title": issue.section_a_title,
                "first_sentence": sec_a.sentences[0] if sec_a and sec_a.sentences else "",
                "last_sentence": sec_a.sentences[-1] if sec_a and sec_a.sentences else "",
            },
            "section_b": {
                "title": issue.section_b_title,
                "first_sentence": sec_b.sentences[0] if sec_b and sec_b.sentences else "",
            },
            "review_question": (
                f"Is the transition from '{issue.section_a_title}' to "
                f"'{issue.section_b_title}' abrupt? "
                f"What context is missing between them?"
            ),
        }

        prompt = (
            f"You are a technical documentation reviewer.\n\n"
            f"Analyze this section transition:\n"
            f"{json.dumps(context, indent=2)}\n\n"
            f"In 1-2 sentences, describe WHY this transition feels abrupt and "
            f"what conceptual bridge is missing. Be specific."
        )

        resp = requests.post(
            ollama_url,
            json={"model": llm_model, "prompt": prompt, "stream": False},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception as e:
        logger.debug(f"LLM flow explanation unavailable: {e}")
    return None
