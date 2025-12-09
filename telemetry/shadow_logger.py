"""
Shadow Mode Logger - Drift Detection Telemetry

Append-only logging for rewrite system observation.
Logs decisions, not content. Protects IP and legal exposure.

DO NOT modify log format without governance review.
DO NOT store full text or suggestions.
"""

import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

TELEMETRY_LOG_PATH = Path(__file__).parent / "rewrite_shadow_log.jsonl"


def shadow_log(
    doc_id: str,
    sentence_idx: int,
    rewrite_attempt: bool,
    rewrite_allowed: bool,
    rewrite_applied: bool,
    justification: str = None
) -> None:
    """
    Log a rewrite decision for shadow mode analysis.
    
    Args:
        doc_id: Document identifier (filename or hash)
        sentence_idx: Sentence index in document
        rewrite_attempt: Whether system attempted rewrite (passed eligibility + justification gates)
        rewrite_allowed: Whether sentence passed eligibility gate
        rewrite_applied: Whether rewrite was actually applied (passed meaning gate)
        justification: Justification trigger if rewrite attempted (from ALLOWED_TRIGGERS)
    
    Format:
        One JSON object per line (JSONL)
        Append-only (no deletions, no retroactive edits)
        No text content stored (triggers only)
    """
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "doc_id": doc_id,
        "idx": sentence_idx,
        "rewrite_attempt": rewrite_attempt,
        "rewrite_allowed": rewrite_allowed,
        "rewrite_applied": rewrite_applied,
        "justification": justification,
    }
    
    try:
        # Ensure directory exists
        TELEMETRY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Append-only write
        with open(TELEMETRY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    
    except Exception as e:
        logger.error(f"Shadow log write failed: {e}")
        # Never block processing on telemetry failure


def get_log_path() -> Path:
    """Return path to shadow log file for analysis scripts."""
    return TELEMETRY_LOG_PATH
