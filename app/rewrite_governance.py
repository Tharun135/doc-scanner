"""
Rewrite Governance Module

This module defines the legal contract for AI-driven text rewrites in the document analysis system.
It enforces that all rewrites are necessity-driven, not style-driven.

DO NOT modify ALLOWED_TRIGGERS without:
1. Documenting the new trigger's necessity criteria
2. Updating tests to validate the trigger
3. Getting explicit governance review approval

This is not a feature toggle system. This is a safety constraint system.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# IMMUTABLE: Legal justifications for AI rewrites
# Any rewrite must map to exactly one of these triggers.
# Style improvements, fluency optimization, and readability enhancements are NOT permitted.
ALLOWED_TRIGGERS = {
    "passive_referent_unclear",    # Passive voice with ambiguous actor
    "pronoun_ambiguity",            # Pronoun without clear antecedent in context
    "acronym_first_use",            # First occurrence requiring expansion
    "ui_reference_confusion",       # UI element label appears twice without markup
    "sequence_ambiguity",           # Technical procedure order unclear
    "vague_quantifier",             # Critical vagueness requiring specificity (some, various, several, many)
    "grammar_tense_error",          # Objective grammar correctness issue
}

# FORBIDDEN: These are NOT valid rewrite triggers
FORBIDDEN_TRIGGERS = {
    "fluency_improvement",
    "readability_enhancement", 
    "style_polish",
    "tone_adjustment",
    "simplification",
    "conciseness",
    "elegance",
    "modernization",
    "consistency",
    "parallelism",
    "sentence_length",
    "clarity_enhancement",  # Too vague - must specify what kind
}

# MAXIMUM REWRITE RATE: Safety ceiling for typical technical documentation
# If rewrite rate exceeds this on representative samples, gates are too loose
MAX_REWRITE_RATE = 0.30  # 30% ceiling


def validate_justification(justification: str) -> None:
    """
    Validate that a rewrite justification is legally permitted.
    
    Raises RuntimeError if justification is not in ALLOWED_TRIGGERS.
    This is a hard contract enforcement - violations should crash the system.
    
    Args:
        justification: The reason string for performing a rewrite
        
    Raises:
        RuntimeError: If justification is not permitted
    """
    if not justification:
        raise RuntimeError("Rewrite attempted without justification - governance violation")
    
    if justification in FORBIDDEN_TRIGGERS:
        raise RuntimeError(
            f"FORBIDDEN rewrite trigger used: '{justification}'. "
            f"Style and fluency improvements are not permitted. "
            f"Only safety-driven rewrites are allowed."
        )
    
    if justification not in ALLOWED_TRIGGERS:
        raise RuntimeError(
            f"Illegal rewrite trigger: '{justification}'. "
            f"Must be one of: {', '.join(ALLOWED_TRIGGERS)}. "
            f"To add a new trigger, update ALLOWED_TRIGGERS with governance review."
        )
    
    logger.debug(f"✓ Rewrite justification validated: {justification}")


def validate_rewrite_result(result: Dict[str, Any]) -> None:
    """
    Validate that a rewrite result complies with governance contract.
    
    Checks:
    - If suggestion differs from original, justification must exist
    - Justification must be in ALLOWED_TRIGGERS
    - Method must indicate proper gating was used
    
    Args:
        result: Result dictionary from AI suggestion engine
        
    Raises:
        RuntimeError: If result violates governance contract
    """
    original = result.get("original", "")
    suggestion = result.get("suggestion", "")
    justification = result.get("justification", "")
    method = result.get("method", "")
    
    # If text was rewritten, must have justification
    if suggestion != original and suggestion:
        if not justification:
            raise RuntimeError(
                f"Rewrite occurred without justification. "
                f"Original: '{original[:50]}...' "
                f"Suggestion: '{suggestion[:50]}...'"
            )
        
        validate_justification(justification)
    
    # Blocked rewrites should not have gone through LLM
    if method in ["eligibility_gate_block", "justification_gate_block"]:
        if suggestion != original:
            logger.warning(
                f"Gate blocked but text still changed - possible bypass. "
                f"Method: {method}"
            )


def validate_batch_stats(stats: Dict[str, Any]) -> None:
    """
    Validate that batch processing statistics comply with governance thresholds.
    
    Args:
        stats: Statistics dictionary with rewrite metrics
        
    Raises:
        RuntimeError: If statistics exceed safety thresholds
    """
    total = stats.get("total_sentences", 0)
    rewrites = stats.get("approved_rewrites", 0)
    
    if total == 0:
        return  # No data to validate
    
    rewrite_rate = rewrites / total
    
    if rewrite_rate > MAX_REWRITE_RATE:
        raise RuntimeError(
            f"Rewrite rate {rewrite_rate:.1%} exceeds safety threshold of {MAX_REWRITE_RATE:.1%}. "
            f"Gates may be too loose or new triggers may have been added improperly. "
            f"Rewrote {rewrites}/{total} sentences."
        )
    
    logger.info(f"✓ Batch rewrite rate {rewrite_rate:.1%} within threshold")


class GovernanceViolation(Exception):
    """Raised when rewrite governance contract is violated."""
    pass
