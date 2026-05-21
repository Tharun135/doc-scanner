"""
Structural Analyzer — extended with Document Intelligence pipeline orchestrator.

The analyze_document_structure() function is kept backward-compatible
(still called from app.py) but now also runs the full document intelligence
stack and returns structural_insights as before.

The new run_document_intelligence() function is the full pipeline entry point
used by the extended /upload route.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Legacy function — preserved for backward compatibility
# ---------------------------------------------------------------------------

def analyze_document_structure(
    sentence_data: List[Dict[str, Any]],
    document_type: str = "general",
) -> List[Dict[str, Any]]:
    """
    Analyzes the document structure by grouping sentences into blocks.
    Identifies high-level issues like flow inconsistencies, run-on sections.
    (Preserved for backward-compat with existing /upload route logic.)
    """
    if not sentence_data:
        return []

    blocks: Dict[int, Dict] = {}
    for sent in sentence_data:
        b_idx = sent.get('block_index', 0)
        if b_idx not in blocks:
            blocks[b_idx] = {
                "tag": sent.get('tag_name', 'p'),
                "sentences": [],
                "issues": 0,
                "text": ""
            }
        blocks[b_idx]["sentences"].append(sent)
        blocks[b_idx]["issues"] += len(sent.get('feedback', []))
        blocks[b_idx]["text"] += " " + sent.get('sentence', '')

    insights = []

    for idx, block in blocks.items():
        sent_count = len(block["sentences"])
        issue_density = block["issues"] / sent_count if sent_count > 0 else 0
        tag = block["tag"]

        if tag == 'p' and sent_count > 6:
            insights.append({
                "type": "structural",
                "severity": "medium",
                "target": f"Paragraph {idx}",
                "message": (
                    f"This paragraph is quite long ({sent_count} sentences). "
                    f"Consider breaking it up to improve readability."
                ),
                "block_index": idx
            })

        if tag.startswith('h') and block["issues"] > 0:
            insights.append({
                "type": "block_meaning",
                "severity": "high",
                "target": f"Section Header: {block['text'][:50]}...",
                "message": (
                    "Found issues in a major section header. "
                    "Critical for document navigation and first impressions."
                ),
                "block_index": idx
            })

        if issue_density > 1.5:
            insights.append({
                "type": "meaning_clarity",
                "severity": "high",
                "target": f"Block {idx}",
                "message": (
                    "This section has a high concentration of writing issues. "
                    "The core meaning may be difficult for the reader to follow."
                ),
                "block_index": idx
            })

    if len(blocks) > 5:
        headers = [b for b in blocks.values() if b["tag"].startswith('h')]
        if len(headers) < 2:
            insights.append({
                "type": "hierarchy",
                "severity": "medium",
                "message": (
                    "The document lacks a clear heading structure. "
                    "Adding headers would help organize different meaning chapters."
                )
            })

    logger.info(f"Structural analysis found {len(insights)} holistic insights")
    return insights


# ---------------------------------------------------------------------------
# New: Full document intelligence pipeline orchestrator
# ---------------------------------------------------------------------------

def run_document_intelligence(
    html_content: str,
    filename: str = "",
    doc_type: str = "unknown",
    review_modes: Optional[List[str]] = None,
    sentence_data: Optional[List[Dict]] = None,
    use_llm: bool = False,
) -> Dict[str, Any]:
    """
    Run the full document intelligence stack and return a serializable dict.

    This is the single entry point called from the /upload route.

    Pipeline:
        DocumentParser → SectionAnalyzer → CrossReferenceValidator
        → ConsistencyEngine → IAAnalyzer → CompletenessDetector
        → FlowAnalyzer → FeedbackAggregator

    Args:
        html_content: Parsed HTML from parse_file().
        filename: Original filename.
        doc_type: Pre-detected type from document_review_gate.
        review_modes: User-selected review modes.
        sentence_data: Sentence-level results (for readability scores).
        use_llm: Enable Layer 3 LLM reasoning for completeness/flow.

    Returns:
        Serializable dict compatible with the document_intelligence API key.
    """
    review_modes = review_modes or ["Style"]
    sentence_data = sentence_data or []

    try:
        from core.document_parser import parse_document
        from core.section_analyzer import analyze_sections
        from core.cross_reference_validator import validate_cross_references
        from core.consistency_engine import analyze_consistency
        from core.ia_analyzer import analyze_ia
        from core.completeness_detector import detect_completeness
        from core.flow_analyzer import analyze_flow
        from core.feedback_aggregator import aggregate

        # Step 1: Build structural model
        model = parse_document(
            html_content,
            filename=filename,
            doc_type=doc_type,
            review_modes=review_modes,
        )

        # Step 2: Determine which analyzers to run based on review modes
        run_style       = "Style" in review_modes or "Release" in review_modes
        run_sme         = "SME" in review_modes or "Release" in review_modes
        run_ux          = "UX" in review_modes or "Release" in review_modes
        run_compliance  = "Compliance" in review_modes or "Translation QA" in review_modes
        run_release     = "Release" in review_modes

        # Always run section analysis (it's the foundation)
        sec_issues  = analyze_sections(model)

        # Cross-reference: SME, Release, Compliance
        xr_issues   = validate_cross_references(model) if (run_sme or run_compliance or run_release) else []

        # Consistency: Style, Compliance, Translation QA
        con_issues  = analyze_consistency(model) if (run_style or run_compliance) else []

        # IA ordering: UX, Release
        ia_issues   = analyze_ia(model) if (run_ux or run_release) else []

        # Completeness: UX, Release
        comp_issues = detect_completeness(model, use_llm=use_llm) if (run_ux or run_release) else []

        # Flow: UX, Style
        fl_issues   = analyze_flow(model, use_llm=use_llm) if (run_ux or run_style) else []

        # Step 3: Aggregate
        result = aggregate(
            model=model,
            section_issues=sec_issues,
            xr_issues=xr_issues,
            con_issues=con_issues,
            ia_issues=ia_issues,
            flow_issues=fl_issues,
            comp_issues=comp_issues,
            sentence_data=sentence_data,
            redundancy_issues=[],
        )

        return result.to_dict()

    except Exception as e:
        logger.error(f"Document intelligence pipeline error: {e}", exc_info=True)
        return {
            "sections": [],
            "section_issues": [],
            "cross_reference_issues": [],
            "consistency_issues": [],
            "ia_issues": [],
            "flow_issues": [],
            "completeness_issues": [],
            "redundancy_issues": [],
            "health_score": None,
            "review_modes_active": review_modes,
            "doc_type": doc_type,
            "total_issues": 0,
            "error": str(e),
        }
