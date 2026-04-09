import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def analyze_document_structure(sentence_data: List[Dict[str, Any]], document_type: str = "general") -> List[Dict[str, Any]]:
    """
    Analyzes the document structure by grouping sentences into blocks (paragraphs/sections).
    Identifies high-level issues like flow inconsistencies, run-on sections, and structural gaps.
    """
    if not sentence_data:
        return []

    # 1. Group sentences into blocks
    blocks = {}
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

    # 2. Analyze individual paragraphs (Blocks)
    for idx, block in blocks.items():
        sent_count = len(block["sentences"])
        issue_density = block["issues"] / sent_count if sent_count > 0 else 0
        tag = block["tag"]

        # Run-on paragraph detection
        if tag == 'p' and sent_count > 6:
            insights.append({
                "type": "structural",
                "severity": "medium",
                "target": f"Paragraph {idx}",
                "message": f"This paragraph is quite long ({sent_count} sentences). Consider breaking it up to improve readability.",
                "block_index": idx
            })

        # Section Header Analysis
        if tag.startswith('h') and block["issues"] > 0:
            insights.append({
                "type": "block_meaning",
                "severity": "high",
                "target": f"Section Header: {block['text'][:50]}...",
                "message": "Found issues in a major section header. Critical for document navigation and first impressions.",
                "block_index": idx
            })

        # High Issue Density
        if issue_density > 1.5:
             insights.append({
                "type": "meaning_clarity",
                "severity": "high",
                "target": f"Block {idx}",
                "message": "This section has a high concentration of writing issues. The core meaning may be difficult for the reader to follow.",
                "block_index": idx
            })

    # 3. Analyze Global Flow (Chapters/Sections)
    # Detect tone shifts or missing summaries
    if len(blocks) > 5:
        headers = [b for b in blocks.values() if b["tag"].startswith('h')]
        if len(headers) < 2:
            insights.append({
                "type": "hierarchy",
                "severity": "medium",
                "message": "The document lacks a clear heading structure. Adding headers would help organize different meaning chapters."
            })

    logger.info(f"🧠 Structural analysis found {len(insights)} holistic insights")
    return insights
