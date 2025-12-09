"""
Atomic Rules Checker
Applies atomic rule-based enforcement using the rule engine.
This integrates with the existing rule system as an additional checker.
"""
import logging
from .loader import load_rules
from .matcher import apply_rules, format_violation_for_ui

logger = logging.getLogger(__name__)

def check(content: str):
    """
    Check content against atomic rules.
    
    This function follows the same signature as other rule checkers
    (grammar_rules.py, style_rules.py, etc.) to integrate seamlessly.
    
    Args:
        content (str): The sentence or content to check
    
    Returns:
        list: List of formatted suggestions/violations
    """
    suggestions = []
    
    # Load atomic rules
    rules = load_rules()
    
    if not rules:
        logger.warning("⚠️ No atomic rules loaded - skipping atomic rule check")
        return suggestions
    
    # Apply rules to the content
    violations = apply_rules(content, rules)
    
    # Format each violation for the UI
    for violation in violations:
        formatted = format_violation_for_ui(violation, content)
        
        # Convert to the format expected by the existing system
        # The existing system expects either strings or dicts with specific keys
        suggestions.append({
            "text": formatted["text"],
            "start": formatted["start"],
            "end": formatted["end"],
            "message": formatted["message"],
            "suggestion": formatted.get("suggestion", ""),
            "severity": formatted["severity"],
            "rule_id": formatted.get("rule_id", ""),
            "category": formatted.get("category", ""),
            "color": formatted["color"]
        })
    
    return suggestions

def check_with_severity_filter(content: str, min_severity: str = "info"):
    """
    Check content but only return violations at or above a certain severity.
    
    Args:
        content (str): The sentence or content to check
        min_severity (str): Minimum severity to include ("error", "warn", or "info")
    
    Returns:
        list: Filtered list of violations
    """
    severity_hierarchy = {"error": 2, "warn": 1, "info": 0}
    min_level = severity_hierarchy.get(min_severity, 0)
    
    all_suggestions = check(content)
    
    return [
        s for s in all_suggestions 
        if severity_hierarchy.get(s.get("severity", "info"), 0) >= min_level
    ]
