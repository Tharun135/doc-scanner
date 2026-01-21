"""
Sentence Split Eligibility Checker
===================================

This module determines when AI should automatically split long sentences.

Philosophy:
-----------
AI SHOULD rewrite only when correctness is more important than completeness.

For complex normative sentences: guidance > automatic split
For simple descriptive sentences: automatic split is safe

The goal is RISK AVOIDANCE, not NLP cleverness.
"""

import re
from typing import Tuple


def can_split_long_sentence(sentence: str) -> Tuple[bool, str]:
    """
    Determines if a long sentence can be safely auto-split by AI.
    
    Returns False (with reason) if ANY of these risks are present:
    - Conditional logic (if, in case, unless, when)
    - Logical OR/AND requirement chains (especially with compliance language)
    - Normative/compliance language combined with conditions
    - Parenthetical technical definitions that bind tightly to nouns
    
    Args:
        sentence: The sentence to evaluate
        
    Returns:
        (can_split: bool, reason: str)
    """
    s = sentence.lower()
    
    # ❌ BLOCKER A: Conditional logic present
    # These almost always break meaning when split
    conditionals = [
        " if ", " in case ", " unless ", " provided that ", 
        " when ", " whenever ", " only if "
    ]
    if any(cond in s for cond in conditionals):
        return False, "Contains conditional logic - manual split safer"
    
    # ❌ BLOCKER B: Logical OR/AND requirement chains
    # These encode alternatives, not sequence
    logical_alternatives = [" or ", " and/or ", " either ", " neither "]
    if any(alt in s for alt in logical_alternatives):
        return False, "Contains logical alternatives - risk of breaking meaning"
    
    # ❌ BLOCKER C: Normative/compliance language
    # Auto-splitting compliance text is a legal/accuracy risk
    normative = [" must ", " shall ", " required ", " mandatory ", " prohibited "]
    if any(norm in s for norm in normative):
        # Extra strict if combined with other risk factors
        if any(cond in s for cond in conditionals) or any(alt in s for alt in logical_alternatives):
            return False, "Normative statement with conditions - manual review required"
        # Pure normative without conditions might still be splittable
        # but we remain conservative
        if len(sentence.split()) > 35:
            return False, "Complex normative requirement - manual split recommended"
    
    # ❌ BLOCKER D: Parenthetical technical definitions
    # These often bind tightly to nouns - splitting can detach meaning
    if "(" in s and ")" in s:
        # Check if parenthetical contains technical acronyms or definitions
        paren_content = re.findall(r'\(([^)]+)\)', sentence)
        for content in paren_content:
            # Technical definitions: uppercase acronyms, "i.e.", "e.g.", or capital letters
            content_upper_count = sum(1 for c in content if c.isupper())
            # If most characters are uppercase or contains definition markers, it's technical
            if (content_upper_count > len(content) * 0.3 or 
                'i.e.' in content.lower() or 
                'e.g.' in content.lower() or
                re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', content)):  # Like "Subject Alternative Name"
                return False, "Contains technical parenthetical - preserve structural binding"
    
    # ✅ POSITIVE SIGNALS: Safe connectors suggest splittability
    # These indicate coordinated actions, not alternatives
    safe_connectors = [" and then ", " before ", " after ", " while ", " which ", " that "]
    has_safe_connector = any(conn in s for conn in safe_connectors)
    
    if has_safe_connector:
        return True, "Contains safe connectors - eligible for split"
    
    # Simple "and" is okay if no other blockers present
    if " and " in s:
        return True, "Simple conjunction - safe to split"
    
    # Default: if no clear signals, be conservative
    return False, "No clear split points identified - guidance recommended"


def always_split_long_sentence(sentence: str) -> Tuple[bool, str]:
    """
    Identifies sentences that should ALWAYS be auto-split (low-risk, high-reward).
    
    Categories that are always safe to split:
    A. Descriptive process chains (X does A and B and C)
    B. Explanation + consequence (X does Y, which results in Z)
    C. Long introductions (X is a concept that...)
    
    Args:
        sentence: The sentence to evaluate
        
    Returns:
        (should_always_split: bool, reason: str)
    """
    s = sentence.lower()
    word_count = len(sentence.split())
    
    # First check: must actually be long enough to warrant splitting
    if word_count < 20:
        return False, "Sentence not long enough to warrant automatic split"
    
    # Blockers: can't be "always split" if these are present
    if _contains_conditionals(sentence):
        return False, "Contains conditionals - not safe for always_split"
    if _contains_normative(sentence):
        return False, "Contains normative language - not safe for always_split"
    
    # ✅ CATEGORY A: Descriptive process chains
    # Pattern: X does A and B and C (multiple "and" connections)
    and_count = s.count(" and ")
    if and_count >= 3:
        # Multiple actions connected by "and" - clear sequence
        return True, "Descriptive process chain - always safe to split"
    
    # ✅ CATEGORY B: Explanation + consequence
    # Pattern: X does Y, which results in Z
    if " which " in s and word_count >= 20:
        # "which" clause typically adds explanation or consequence
        return True, "Explanation with consequence clause - always safe to split"
    
    # ✅ CATEGORY C: Long introductions
    # Pattern: X is a concept/approach/method that...
    intro_patterns = [
        r"\bis a (concept|approach|method|technique|process|system|tool|feature)\b",
        r"\bprovides (information|details|guidance|instructions) (on|about|for)\b",
        r"\bdescribes (how|the|a)\b"
    ]
    for pattern in intro_patterns:
        if re.search(pattern, s) and word_count >= 20:
            return True, "Long introductory/descriptive sentence - always safe to split"
    
    return False, "Does not match 'always split' categories"


def _contains_conditionals(sentence: str) -> bool:
    """Helper: Check if sentence contains conditional logic."""
    s = sentence.lower()
    conditionals = [" if ", " in case ", " unless ", " when ", " whenever "]
    return any(cond in s for cond in conditionals)


def _contains_normative(sentence: str) -> bool:
    """Helper: Check if sentence contains normative/compliance language."""
    s = sentence.lower()
    normative = [" must ", " shall ", " required ", " mandatory "]
    return any(norm in s for norm in normative)


def get_split_decision(sentence: str) -> Tuple[str, str]:
    """
    Master function: Determines the split strategy for a long sentence.
    
    Returns:
        (decision: str, reason: str)
        
    decision can be:
        "always_split"          - Low-risk, high-reward, always auto-split
        "eligible_split"        - Safe to split, proceed with AI
        "semantic_explanation"  - Complex, explain meaning but don't rewrite
        "guidance_only"         - Risk present, provide manual guidance only
    """
    # Check if it should always be split (highest priority)
    always_split, always_reason = always_split_long_sentence(sentence)
    if always_split:
        return "always_split", always_reason
    
    # Check if it's eligible for AI split
    can_split, can_reason = can_split_long_sentence(sentence)
    if can_split:
        return "eligible_split", can_reason
    
    # Check if it's semantically complex (warrants explanation)
    if is_semantically_complex(sentence):
        return "semantic_explanation", "Complex logic warrants semantic explanation"
    
    # Default: guidance only
    return "guidance_only", can_reason


# ============================================================================
# Semantic Complexity Detection
# ============================================================================

def is_semantically_complex(sentence: str) -> bool:
    """
    Determines if a sentence is semantically complex enough to warrant
    AI semantic explanation (not rewriting, just explaining).
    
    Complex sentences have:
    - Conditional logic (if, unless, when)
    - Logical alternatives (or, either)
    - Compliance/normative language (must, shall)
    - Multiple clauses with dependencies
    
    Returns:
        True if sentence is semantically complex
    """
    s = sentence.lower()
    
    # Has conditional logic
    if _contains_conditionals(sentence):
        return True
    
    # Has logical alternatives
    if " or " in s or " either " in s or " neither " in s:
        return True
    
    # Has normative language with conditions
    if _contains_normative(sentence) and (
        _contains_conditionals(sentence) or " or " in s
    ):
        return True
    
    # Has technical parentheticals
    if "(" in s and ")" in s:
        paren_content = re.findall(r'\(([^)]+)\)', sentence)
        for content in paren_content:
            content_upper_count = sum(1 for c in content if c.isupper())
            if content_upper_count > len(content) * 0.3:
                return True
    
    return False


# ============================================================================
# Semantic Explanation (AI explains meaning without rewriting)
# ============================================================================

def get_semantic_explanation_prompt(sentence: str) -> str:
    """
    Returns the prompt for AI to explain semantic structure.
    
    This prompt is STRICTLY constrained:
    - No rewriting
    - No suggestions
    - No advisory language
    - Only interpretation
    """
    return f"""You are acting as a documentation reviewer.

Explain the meaning and logical structure of the following sentence.

Rules:
- Do NOT rewrite the sentence.
- Do NOT suggest changes or improvements.
- Do NOT add new requirements or assumptions.
- Only explain how the ideas, conditions, and obligations relate to each other.
- Use neutral, factual language.

Sentence:
"{sentence}"

Return a short explanation in plain English."""


def validate_semantic_explanation(original: str, explanation: str) -> tuple[bool, str]:
    """
    Validates that semantic explanation is safe to show.
    
    Checks:
    1. No rewrite behavior (not just restating the sentence)
    2. No advisory language (should, consider, etc.)
    3. Entity preservation (mentions core terms from original)
    4. No new obligations (no invented requirements)
    
    Returns:
        (is_valid: bool, reason: str)
    """
    if not explanation or len(explanation.strip()) < 10:
        return False, "Explanation too short or empty"
    
    exp_lower = explanation.lower()
    orig_lower = original.lower()
    
    # Rule 1: Reject if looks like a rewrite (explanation is too similar to original)
    # Simple heuristic: if >60% of original words appear in explanation in same order
    orig_words = orig_lower.split()
    exp_words = exp_lower.split()
    common_ordered = sum(1 for w in orig_words if w in exp_words and len(w) > 3)
    similarity = common_ordered / len(orig_words) if orig_words else 0
    
    if similarity > 0.7:
        return False, "Explanation appears to be a rewrite"
    
    # Rule 2: Reject if contains advisory language
    advisory_terms = [
        "should", "consider", "recommend", "better to", "you can", 
        "try to", "it's better", "instead", "prefer"
    ]
    if any(term in exp_lower for term in advisory_terms):
        return False, "Contains advisory language"
    
    # Rule 3: Entity preservation - explanation should reference key terms
    # Extract meaningful words (>3 chars, not common)
    common_words = {'the', 'this', 'that', 'with', 'from', 'have', 'been', 'will', 'they', 'their', 'there'}
    orig_key_words = {w for w in orig_words if len(w) > 3 and w not in common_words}
    exp_key_words = {w for w in exp_words if len(w) > 3 and w not in common_words}
    
    overlap = orig_key_words & exp_key_words
    if len(overlap) < 2:  # Should reference at least 2 key terms
        return False, "Does not reference key entities from original"
    
    # Rule 4: No new obligations - reject if explanation adds normative language
    orig_normative = {"must", "shall", "required", "mandatory"}
    exp_normative_count = sum(1 for term in orig_normative if term in exp_lower)
    orig_normative_count = sum(1 for term in orig_normative if term in orig_lower)
    
    if exp_normative_count > orig_normative_count:
        return False, "Introduces new obligations not in original"
    
    return True, "Valid semantic explanation"


# ============================================================================
# UI Message Templates - Reviewer-Centric Language
# ============================================================================

def get_ui_message(decision: str, word_count: int) -> dict:
    """
    Returns appropriate UI messaging based on split decision.
    
    Key principle: Never imply AI "failed". Always imply reviewer "decided".
    """
    if decision == "always_split":
        return {
            "title": "Suggested rewrite (reviewer-approved)",
            "explanation": f"This sentence ({word_count} words) was split to improve readability while preserving meaning.",
            "action_label": "Rewrite Applied"
        }
    
    elif decision == "eligible_split":
        return {
            "title": "Suggested rewrite",
            "explanation": f"This sentence ({word_count} words) can be split into shorter sentences for better readability.",
            "action_label": "AI Suggestion"
        }
    
    elif decision == "semantic_explanation":
        return {
            "title": "🧠 Semantic explanation (AI-assisted)",
            "explanation": "AI explains the meaning and logical structure without making changes.",
            "note": "No changes are suggested because this sentence contains complex logic that requires careful manual review.",
            "action_label": "Semantic Analysis"
        }
    
    else:  # guidance_only
        return {
            "title": "Reviewer guidance",
            "explanation": f"This sentence ({word_count} words) contains complex logic that requires careful manual review.",
            "details": "Splitting it automatically could change its meaning.",
            "recommendation": (
                "**Recommended action:**\n"
                "Split it manually into:\n"
                "• one sentence for the main requirement\n"
                "• one sentence for conditions or alternatives"
            ),
            "action_label": "Manual Review Recommended"
        }
