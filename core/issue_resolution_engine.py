"""
Issue Resolution Engine - Deterministic Decision System

This module enforces the core principle:
> Never ask the LLM to decide what to do.
> Force the decision in code.
> Use the LLM only to express it well.

Every issue maps to exactly one resolution class.
Every resolution class has a deterministic template.
The LLM only adapts the template to specific content.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    """Every detected issue maps to exactly one of these types."""
    PASSIVE_VOICE = "passive_voice"
    LONG_SENTENCE = "long_sentence"
    VAGUE_TERM = "vague_term"
    MISSING_PREREQUISITE = "missing_prerequisite"
    DENSE_STEP = "dense_step"
    STEP_ORDER_PROBLEM = "step_order_problem"
    UNDEFINED_ACRONYM = "undefined_acronym"
    INCONSISTENT_TERMINOLOGY = "inconsistent_terminology"
    MIXED_TENSE = "mixed_tense"
    MISSING_INTRODUCTION = "missing_introduction"


class ResolutionClass(Enum):
    """Every issue type maps to exactly one resolution class."""
    REWRITE_ACTIVE = "rewrite_active"
    SIMPLIFY_SENTENCE = "simplify_sentence"
    REPLACE_WITH_SPECIFIC = "replace_with_specific"
    ASK_FOR_PREREQUISITES = "ask_for_prerequisites"
    BREAK_INTO_STEPS = "break_into_steps"
    REORDER_GUIDANCE = "reorder_guidance"
    DEFINE_ACRONYM = "define_acronym"
    STANDARDIZE_TERM = "standardize_term"
    UNIFY_TENSE = "unify_tense"
    ADD_INTRODUCTION = "add_introduction"


class IssueSeverity(Enum):
    """Separate blocking from advisory issues."""
    BLOCKING = "blocking"  # User cannot proceed effectively without fixing
    ADVISORY = "advisory"  # Improvement suggestion, not required


@dataclass
class ResolutionTemplate:
    """
    Deterministic template for each resolution class.
    LLM only adapts this to specific content, never invents structure.
    """
    resolution_class: ResolutionClass
    severity: IssueSeverity
    deterministic_fallback: str  # What to show if LLM fails or RAG is weak
    action_required: str  # Clear next step for the user
    explanation_template: str  # Template for LLM to adapt
    value_threshold: float = 0.3  # Minimum required change from original
    
    def get_fallback_response(self, context: Dict[str, Any]) -> str:
        """Return deterministic guidance when AI cannot help."""
        return self.deterministic_fallback


# ============================================================================
# ISSUE → RESOLUTION CLASS MAPPING (Core Decision Logic)
# ============================================================================

ISSUE_TO_RESOLUTION: Dict[IssueType, ResolutionClass] = {
    IssueType.PASSIVE_VOICE: ResolutionClass.REWRITE_ACTIVE,
    IssueType.LONG_SENTENCE: ResolutionClass.SIMPLIFY_SENTENCE,
    IssueType.VAGUE_TERM: ResolutionClass.REPLACE_WITH_SPECIFIC,
    IssueType.MISSING_PREREQUISITE: ResolutionClass.ASK_FOR_PREREQUISITES,
    IssueType.DENSE_STEP: ResolutionClass.BREAK_INTO_STEPS,
    IssueType.STEP_ORDER_PROBLEM: ResolutionClass.REORDER_GUIDANCE,
    IssueType.UNDEFINED_ACRONYM: ResolutionClass.DEFINE_ACRONYM,
    IssueType.INCONSISTENT_TERMINOLOGY: ResolutionClass.STANDARDIZE_TERM,
    IssueType.MIXED_TENSE: ResolutionClass.UNIFY_TENSE,
    IssueType.MISSING_INTRODUCTION: ResolutionClass.ADD_INTRODUCTION,
}


# ============================================================================
# RESOLUTION TEMPLATES (Deterministic Fallbacks)
# ============================================================================

RESOLUTION_TEMPLATES: Dict[ResolutionClass, ResolutionTemplate] = {
    ResolutionClass.REWRITE_ACTIVE: ResolutionTemplate(
        resolution_class=ResolutionClass.REWRITE_ACTIVE,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This sentence uses passive voice. Active voice is clearer and more direct.\n\n"
            "Action: Rewrite to show who performs the action.\n"
            "Example: 'The file was opened' → 'The system opens the file'"
        ),
        action_required="Rewrite in active voice",
        explanation_template=(
            "This uses passive voice. For technical writing, active voice is clearer.\n"
            "Suggested rewrite: {rewrite}\n"
            "This makes it clear who performs the action."
        )
    ),
    
    ResolutionClass.SIMPLIFY_SENTENCE: ResolutionTemplate(
        resolution_class=ResolutionClass.SIMPLIFY_SENTENCE,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This sentence combines more than one idea, making it harder to follow.\n\n"
            "Action: Break this into 2-3 shorter sentences.\n"
            "Each sentence should convey one clear idea."
        ),
        action_required="Break into shorter sentences",
        explanation_template=(
            "This sentence is complex ({word_count} words).\n"
            "Suggested breakdown:\n{breakdown}\n"
            "This improves readability and comprehension."
        )
    ),
    
    ResolutionClass.REPLACE_WITH_SPECIFIC: ResolutionTemplate(
        resolution_class=ResolutionClass.REPLACE_WITH_SPECIFIC,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This uses a vague term that doesn't give the reader specific information.\n\n"
            "Action: Replace with a concrete term or number.\n"
            "Example: 'several times' → 'three times' or 'every 5 seconds'"
        ),
        action_required="Replace with specific term",
        explanation_template=(
            "'{vague_term}' is vague.\n"
            "Suggested replacement: {specific_term}\n"
            "This gives readers concrete information."
        )
    ),
    
    ResolutionClass.ASK_FOR_PREREQUISITES: ResolutionTemplate(
        resolution_class=ResolutionClass.ASK_FOR_PREREQUISITES,
        severity=IssueSeverity.BLOCKING,
        deterministic_fallback=(
            "This procedure lacks a Prerequisites section. Users need to know what's required before starting.\n\n"
            "Action: Add a 'Prerequisites' section at the start listing:\n"
            "- Required permissions or access\n"
            "- Necessary tools or software\n"
            "- Required knowledge or prior steps"
        ),
        action_required="Add Prerequisites section",
        explanation_template=(
            "Add a Prerequisites section before the procedure begins.\n"
            "Include: {suggested_prerequisites}\n"
            "This ensures users are prepared before starting."
        )
    ),
    
    ResolutionClass.BREAK_INTO_STEPS: ResolutionTemplate(
        resolution_class=ResolutionClass.BREAK_INTO_STEPS,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This step combines multiple actions. As a first-time user, this is hard to follow.\n\n"
            "Action: Split into separate numbered steps.\n"
            "Each step should contain:\n"
            "1. One clear action\n"
            "2. Expected result or verification"
        ),
        action_required="Split into multiple steps",
        explanation_template=(
            "This step combines {action_count} actions.\n"
            "Suggested breakdown:\n{step_breakdown}\n"
            "Each step now has one clear action and expected result."
        )
    ),
    
    ResolutionClass.REORDER_GUIDANCE: ResolutionTemplate(
        resolution_class=ResolutionClass.REORDER_GUIDANCE,
        severity=IssueSeverity.BLOCKING,
        deterministic_fallback=(
            "These steps appear out of logical order. Users may fail if they follow them as written.\n\n"
            "Action: Reorder steps to match dependencies.\n"
            "Rule: Prerequisites must come before dependent actions."
        ),
        action_required="Reorder steps logically",
        explanation_template=(
            "The current order creates a dependency problem:\n"
            "{dependency_issue}\n\n"
            "Suggested order: {suggested_order}\n"
            "This ensures prerequisites are met before dependent actions."
        )
    ),
    
    ResolutionClass.DEFINE_ACRONYM: ResolutionTemplate(
        resolution_class=ResolutionClass.DEFINE_ACRONYM,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This acronym appears without definition. First-time users may not know what it means.\n\n"
            "Action: Define on first use in this format:\n"
            "Full Term (ACRONYM)\n"
            "Example: 'Application Programming Interface (API)'"
        ),
        action_required="Define acronym on first use",
        explanation_template=(
            "'{acronym}' needs definition.\n"
            "Suggested: {full_term} ({acronym})\n"
            "This helps readers who are unfamiliar with the term."
        )
    ),
    
    ResolutionClass.STANDARDIZE_TERM: ResolutionTemplate(
        resolution_class=ResolutionClass.STANDARDIZE_TERM,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This document uses multiple terms for the same concept, which can confuse readers.\n\n"
            "Action: Choose one canonical term and use it consistently.\n"
            "Example: Always use 'user' instead of mixing 'user', 'customer', 'client'"
        ),
        action_required="Use consistent terminology",
        explanation_template=(
            "Use '{canonical_term}' consistently instead of '{variant}'.\n"
            "Found {count} inconsistent uses.\n"
            "Consistency helps readers build mental models."
        )
    ),
    
    ResolutionClass.UNIFY_TENSE: ResolutionTemplate(
        resolution_class=ResolutionClass.UNIFY_TENSE,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This document mixes verb tenses, which can confuse the reader about timing.\n\n"
            "Action: Choose one tense and use it consistently.\n"
            "For procedures: Use present tense ('Click the button')\n"
            "For reports: Use past tense ('The system processed the request')"
        ),
        action_required="Use consistent verb tense",
        explanation_template=(
            "Use {recommended_tense} tense consistently.\n"
            "Current mix: {tense_examples}\n"
            "Consistent tense clarifies when actions occur."
        )
    ),
    
    ResolutionClass.ADD_INTRODUCTION: ResolutionTemplate(
        resolution_class=ResolutionClass.ADD_INTRODUCTION,
        severity=IssueSeverity.ADVISORY,
        deterministic_fallback=(
            "This document lacks an introduction. Users need context before diving into details.\n\n"
            "Action: Add an Introduction section that answers:\n"
            "- What is this document about?\n"
            "- Who should read it?\n"
            "- What will the reader accomplish?"
        ),
        action_required="Add introduction section",
        explanation_template=(
            "Add an Introduction section covering:\n{intro_elements}\n"
            "This gives readers context and sets expectations."
        )
    ),
}


# ============================================================================
# ISSUE SEVERITY MAPPING
# ============================================================================

ISSUE_SEVERITY: Dict[IssueType, IssueSeverity] = {
    IssueType.PASSIVE_VOICE: IssueSeverity.ADVISORY,
    IssueType.LONG_SENTENCE: IssueSeverity.ADVISORY,
    IssueType.VAGUE_TERM: IssueSeverity.ADVISORY,
    IssueType.MISSING_PREREQUISITE: IssueSeverity.BLOCKING,
    IssueType.DENSE_STEP: IssueSeverity.ADVISORY,
    IssueType.STEP_ORDER_PROBLEM: IssueSeverity.BLOCKING,
    IssueType.UNDEFINED_ACRONYM: IssueSeverity.ADVISORY,
    IssueType.INCONSISTENT_TERMINOLOGY: IssueSeverity.ADVISORY,
    IssueType.MIXED_TENSE: IssueSeverity.ADVISORY,
    IssueType.MISSING_INTRODUCTION: IssueSeverity.ADVISORY,
}


# ============================================================================
# VALUE VALIDATION (Ensure LLM output is useful)
# ============================================================================

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts (0.0 to 1.0)."""
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def contains_action(text: str) -> bool:
    """Check if text contains actionable guidance."""
    action_indicators = [
        'rewrite', 'replace', 'change', 'add', 'remove', 'split',
        'break', 'combine', 'move', 'define', 'clarify', 'specify',
        'use', 'avoid', 'consider', 'ensure', 'verify'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in action_indicators)


def is_value_added(original: str, suggestion: str, threshold: float = 0.3) -> bool:
    """
    Validate that a suggestion adds value.
    
    Reject if:
    - Too similar to original (repeats text)
    - Lacks actionable guidance
    - Contains only vague suggestions
    """
    if not suggestion or not suggestion.strip():
        return False
    
    # Check similarity
    similarity = calculate_similarity(original, suggestion)
    if similarity > (1.0 - threshold):
        return False
    
    # Check for actionable content
    if not contains_action(suggestion):
        return False
    
    # Check for hedge words without action
    hedge_words = ['consider', 'might', 'possibly', 'perhaps', 'maybe']
    suggestion_lower = suggestion.lower()
    
    has_hedge = any(word in suggestion_lower for word in hedge_words)
    has_concrete_action = any(word in suggestion_lower for word in [
        'rewrite to', 'replace with', 'change to', 'add', 'remove', 'use'
    ])
    
    # If it only hedges without concrete action, reject
    if has_hedge and not has_concrete_action:
        return False
    
    return True


# ============================================================================
# RESOLUTION ENGINE (Main Logic)
# ============================================================================

class IssueResolutionEngine:
    """
    Deterministic decision engine.
    
    - Maps issues to resolution classes
    - Provides deterministic fallbacks
    - Validates LLM output
    - Never lets the model "figure things out"
    """
    
    def __init__(self):
        self.issue_to_resolution = ISSUE_TO_RESOLUTION
        self.resolution_templates = RESOLUTION_TEMPLATES
        self.issue_severity = ISSUE_SEVERITY
    
    def classify_issue(self, issue_data: Dict[str, Any]) -> Optional[IssueType]:
        """
        Map detected issue to IssueType.
        If no clean mapping exists, return None (don't show to user).
        """
        # Extract issue indicators from the data
        feedback = issue_data.get('feedback', '').lower()
        rule_id = issue_data.get('rule_id', '').lower()
        
        # Only classify if we have strong signal
        if not feedback and not rule_id:
            return None
        
        # Map based on patterns (order matters - most specific first)
        if 'passive' in feedback or 'passive_voice' in rule_id:
            return IssueType.PASSIVE_VOICE
        
        if 'prerequisite' in feedback or 'missing prerequisite' in rule_id:
            return IssueType.MISSING_PREREQUISITE
        
        if 'acronym' in feedback or 'undefined acronym' in rule_id:
            return IssueType.UNDEFINED_ACRONYM
        
        if 'terminology' in feedback or 'inconsistent' in feedback or 'terminology' in rule_id:
            return IssueType.INCONSISTENT_TERMINOLOGY
        
        if 'mixed tense' in feedback or 'mixed tense' in rule_id:
            return IssueType.MIXED_TENSE
        
        if 'introduction' in feedback or 'missing introduction' in rule_id:
            return IssueType.MISSING_INTRODUCTION
        
        if 'dense' in feedback or 'multiple actions' in feedback or 'dense_step' in rule_id:
            return IssueType.DENSE_STEP
        
        if ('order' in feedback and 'step' in feedback) or 'step_order' in rule_id:
            return IssueType.STEP_ORDER_PROBLEM
        
        # Vague terms - check for specific words
        if 'vague' in feedback or 'very' in feedback or any(term in feedback for term in ['some', 'several', 'various', 'stuff', 'things', 'very']):
            # But only if it's specifically about vague terms or adverbs
            if 'vague' in feedback or 'vague_term' in rule_id or 'very' in feedback or 'removing' in feedback:
                return IssueType.VAGUE_TERM
        
        # Long sentence - be specific to avoid false matches
        if ('long' in feedback and 'sentence' in feedback) or 'break' in feedback and 'sentence' in feedback:
            return IssueType.LONG_SENTENCE
        
        # No clean mapping = don't show this issue
        # This is intentional - we only show issues we can handle well
        return None
    
    def get_resolution(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get deterministic resolution for an issue.
        
        Returns:
        - resolution_class: What type of fix is needed
        - severity: blocking or advisory
        - fallback_text: Guaranteed useful guidance
        - action_required: Clear next step
        """
        resolution_class = self.issue_to_resolution.get(issue_type)
        if not resolution_class:
            return None
        
        template = self.resolution_templates[resolution_class]
        severity = self.issue_severity.get(issue_type, IssueSeverity.ADVISORY)
        
        return {
            'resolution_class': resolution_class.value,
            'severity': severity.value,
            'fallback_text': template.get_fallback_response(context),
            'action_required': template.action_required,
            'template': template.explanation_template,
            'value_threshold': template.value_threshold,
        }
    
    def validate_suggestion(
        self,
        original_text: str,
        suggested_text: str,
        resolution_class: ResolutionClass
    ) -> bool:
        """
        Validate that LLM-generated suggestion meets quality threshold.
        """
        template = self.resolution_templates.get(resolution_class)
        if not template:
            return False
        
        return is_value_added(
            original_text,
            suggested_text,
            threshold=template.value_threshold
        )
    
    def get_fallback_response(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> str:
        """
        Get deterministic fallback when AI cannot help.
        Guaranteed to be useful.
        """
        resolution = self.get_resolution(issue_type, context)
        if not resolution:
            return "Unable to provide specific guidance for this issue."
        
        return resolution['fallback_text']


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_resolution_engine() -> IssueResolutionEngine:
    """Get singleton instance of resolution engine."""
    return IssueResolutionEngine()


def resolve_issue(issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Main entry point: resolve an issue deterministically.
    
    Returns resolution or None if issue doesn't map cleanly.
    """
    engine = get_resolution_engine()
    
    # Classify the issue
    issue_type = engine.classify_issue(issue_data)
    if not issue_type:
        return None  # Don't show issues that don't map cleanly
    
    # Get deterministic resolution
    context = {
        'sentence': issue_data.get('context', ''),
        'feedback': issue_data.get('feedback', ''),
        'document_type': issue_data.get('document_type', 'general'),
    }
    
    resolution = engine.get_resolution(issue_type, context)
    if not resolution:
        return None
    
    # Add issue type info
    resolution['issue_type'] = issue_type.value
    resolution['context'] = context
    
    return resolution
