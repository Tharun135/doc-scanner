"""
Feedback Aggregator
====================

Merges findings from all document-intelligence layers into a single
DocumentIntelligenceResult. This is what gets serialized into the
API response under the "document_intelligence" key.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from core.document_parser import DocumentModel, Section
from core.section_analyzer import SectionIssue
from core.cross_reference_validator import XRIssue
from core.consistency_engine import ConsistencyIssue
from core.ia_analyzer import IAIssue
from core.completeness_detector import CompletenessIssue
from core.flow_analyzer import FlowIssue

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Health Score
# ---------------------------------------------------------------------------

@dataclass
class DocumentHealthScore:
    structure: int      # SEC-* violations → heading quality, section hierarchy
    consistency: int    # CON-* violations
    completeness: int   # COMP-* missing elements
    readability: int    # Flesch scores from sentence analysis
    flow: int           # FL-* + IA-* violations
    cross_references: int  # XR-* violations
    redundancy: int     # DUP-* (placeholder until embedding layer)
    total: int = 0

    def compute_total(self) -> None:
        weights = {
            "structure": 0.20,
            "consistency": 0.15,
            "completeness": 0.20,
            "readability": 0.15,
            "flow": 0.15,
            "cross_references": 0.10,
            "redundancy": 0.05,
        }
        self.total = round(
            self.structure * weights["structure"] +
            self.consistency * weights["consistency"] +
            self.completeness * weights["completeness"] +
            self.readability * weights["readability"] +
            self.flow * weights["flow"] +
            self.cross_references * weights["cross_references"] +
            self.redundancy * weights["redundancy"]
        )


# ---------------------------------------------------------------------------
# Section Summary (for UI)
# ---------------------------------------------------------------------------

@dataclass
class SectionSummary:
    id: str
    title: str
    level: int
    word_count: int
    issue_count: int
    issues: List[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Full Result
# ---------------------------------------------------------------------------

@dataclass
class DocumentIntelligenceResult:
    sections: List[SectionSummary] = field(default_factory=list)
    section_issues: List[dict] = field(default_factory=list)
    cross_reference_issues: List[dict] = field(default_factory=list)
    consistency_issues: List[dict] = field(default_factory=list)
    ia_issues: List[dict] = field(default_factory=list)
    flow_issues: List[dict] = field(default_factory=list)
    completeness_issues: List[dict] = field(default_factory=list)
    redundancy_issues: List[dict] = field(default_factory=list)
    health_score: Optional[DocumentHealthScore] = None
    review_modes_active: List[str] = field(default_factory=list)
    doc_type: str = "unknown"
    total_issues: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-safe dictionary."""
        return {
            "sections": [asdict(s) for s in self.sections],
            "section_issues": self.section_issues,
            "cross_reference_issues": self.cross_reference_issues,
            "consistency_issues": self.consistency_issues,
            "ia_issues": self.ia_issues,
            "flow_issues": self.flow_issues,
            "completeness_issues": self.completeness_issues,
            "redundancy_issues": self.redundancy_issues,
            "health_score": asdict(self.health_score) if self.health_score else None,
            "review_modes_active": self.review_modes_active,
            "doc_type": self.doc_type,
            "total_issues": self.total_issues,
        }


# ---------------------------------------------------------------------------
# Score calculator
# ---------------------------------------------------------------------------

def _score_from_issues(issues: list, max_penalty: int = 30) -> int:
    """
    Convert a list of issues into a 0-100 score.

    major issues → 15 pts each
    minor issues → 7 pts each
    info issues  → 2 pts each
    """
    penalty = 0
    for issue in issues:
        sev = issue.get("severity", "minor") if isinstance(issue, dict) else getattr(issue, "severity", "minor")
        if sev == "major":
            penalty += 15
        elif sev == "minor":
            penalty += 7
        else:
            penalty += 2
    return max(0, 100 - min(penalty, max_penalty))


def _avg_readability(sentence_data: List[Dict]) -> int:
    """Compute average Flesch reading ease from sentence-level analysis."""
    scores = []
    for s in sentence_data:
        for fb in s.get("feedback", []):
            if isinstance(fb, dict):
                rs = fb.get("readability_scores", {})
                if "flesch_reading_ease" in rs:
                    scores.append(rs["flesch_reading_ease"])
    if not scores:
        return 65  # Default: average readability
    avg = sum(scores) / len(scores)
    return max(0, min(100, int(avg)))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def aggregate(
    model: DocumentModel,
    section_issues: List[SectionIssue],
    xr_issues: List[XRIssue],
    con_issues: List[ConsistencyIssue],
    ia_issues: List[IAIssue],
    flow_issues: List[FlowIssue],
    comp_issues: List[CompletenessIssue],
    sentence_data: Optional[List[Dict]] = None,
    redundancy_issues: Optional[List[dict]] = None,
) -> DocumentIntelligenceResult:
    """
    Merge all layer findings into a DocumentIntelligenceResult.

    Args:
        model: Parsed DocumentModel.
        section_issues: From section_analyzer.
        xr_issues: From cross_reference_validator.
        con_issues: From consistency_engine.
        ia_issues: From ia_analyzer.
        flow_issues: From flow_analyzer.
        comp_issues: From completeness_detector.
        sentence_data: Sentence-level analysis results (for readability scores).
        redundancy_issues: From embedding_indexer (future layer 2).
    """
    sentence_data = sentence_data or []
    redundancy_issues = redundancy_issues or []

    # Convert dataclass issues to dicts (handles both old-style and dataclass)
    def _to_dict(obj) -> dict:
        if isinstance(obj, dict):
            return obj
        return asdict(obj)

    sec_dicts  = [_to_dict(i) for i in section_issues]
    xr_dicts   = [_to_dict(i) for i in xr_issues]
    con_dicts  = [_to_dict(i) for i in con_issues]
    ia_dicts   = [_to_dict(i) for i in ia_issues]
    fl_dicts   = [_to_dict(i) for i in flow_issues]
    comp_dicts = [_to_dict(i) for i in comp_issues]

    # Build section summaries
    # Group section issues by section_id
    issues_by_sec: Dict[str, List[dict]] = {}
    for issue in sec_dicts + xr_dicts + con_dicts + ia_dicts + fl_dicts + comp_dicts:
        sid = issue.get("section_id") or "__doc__"
        issues_by_sec.setdefault(sid, []).append(issue)

    section_summaries = []
    for sec in model.sections:
        sec_issues = issues_by_sec.get(sec.id, [])
        section_summaries.append(SectionSummary(
            id=sec.id,
            title=sec.title,
            level=sec.level,
            word_count=sec.word_count,
            issue_count=len(sec_issues),
            issues=sec_issues[:5],  # Top 5 per section for UI
        ))

    # Compute health score
    readability = _avg_readability(sentence_data)
    health = DocumentHealthScore(
        structure=_score_from_issues(sec_dicts),
        consistency=_score_from_issues(con_dicts),
        completeness=_score_from_issues(comp_dicts),
        readability=readability,
        flow=_score_from_issues(fl_dicts + ia_dicts),
        cross_references=_score_from_issues(xr_dicts),
        redundancy=_score_from_issues(redundancy_issues) if redundancy_issues else 95,
    )
    health.compute_total()

    all_issues = (sec_dicts + xr_dicts + con_dicts + ia_dicts + fl_dicts
                  + comp_dicts + redundancy_issues)

    result = DocumentIntelligenceResult(
        sections=section_summaries,
        section_issues=sec_dicts,
        cross_reference_issues=xr_dicts,
        consistency_issues=con_dicts,
        ia_issues=ia_dicts,
        flow_issues=fl_dicts,
        completeness_issues=comp_dicts,
        redundancy_issues=redundancy_issues,
        health_score=health,
        review_modes_active=model.review_modes,
        doc_type=model.doc_type,
        total_issues=len(all_issues),
    )

    logger.info(
        f"FeedbackAggregator: total={result.total_issues} issues, "
        f"health={health.total}/100"
    )
    return result
