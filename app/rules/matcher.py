"""
Rule Matcher Module
Applies atomic rules to sentences using regex pattern matching.
Returns violations with severity-based classification.
"""
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def apply_rules(sentence: str, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply all rules to a sentence and return violations.
    
    Args:
        sentence (str): The sentence text to check
        rules (list): List of rule dictionaries from loader
    
    Returns:
        list: List of violation dictionaries with structure:
              {
                "rule_id": str,
                "category": str,
                "severity": str (error|warn|info),
                "message": str,
                "suggestion": str,
                "matched_text": str (the actual text that matched)
              }
    """
    violations = []
    
    if not sentence or not sentence.strip():
        return violations
    
    for rule in rules:
        try:
            pattern = rule.get("regex", "")
            if not pattern:
                continue
            
            # Perform case-insensitive regex search
            matches = re.finditer(pattern, sentence, flags=re.IGNORECASE)
            
            for match in matches:
                violation = {
                    "rule_id": rule.get("rule_id", "UNKNOWN"),
                    "category": rule.get("category", "general"),
                    "severity": rule.get("severity", "warn"),
                    "message": rule.get("message", "Style violation detected"),
                    "suggestion": rule.get("suggestion", ""),
                    "matched_text": match.group(0),
                    "match_start": match.start(),
                    "match_end": match.end()
                }
                violations.append(violation)
                
                # Log error-level violations
                if violation["severity"] == "error":
                    logger.debug(f"🔴 ERROR: {violation['rule_id']} - {violation['message']} | Matched: '{match.group(0)}'")
        
        except re.error as e:
            logger.error(f"❌ Invalid regex in rule {rule.get('rule_id', 'UNKNOWN')}: {e}")
        except Exception as e:
            logger.error(f"❌ Error applying rule {rule.get('rule_id', 'UNKNOWN')}: {e}")
    
    return violations

def format_violation_for_ui(violation: Dict[str, Any], sentence: str) -> Dict[str, Any]:
    """
    Format a violation for UI display with color coding and structured data.
    
    Args:
        violation (dict): Violation dictionary from apply_rules
        sentence (str): The full sentence text
    
    Returns:
        dict: Formatted for existing UI structure:
              {
                "text": str (sentence),
                "start": int,
                "end": int,
                "message": str,
                "suggestion": str,
                "severity": str,
                "rule_id": str,
                "category": str,
                "color": str (red|yellow|grey)
              }
    """
    # Map severity to color
    severity_to_color = {
        "error": "red",
        "warn": "yellow",
        "info": "grey"
    }
    
    severity = violation.get("severity", "warn")
    color = severity_to_color.get(severity, "yellow")
    
    return {
        "text": sentence,
        "start": violation.get("match_start", 0),
        "end": violation.get("match_end", len(sentence)),
        "message": violation.get("message", ""),
        "suggestion": violation.get("suggestion", ""),
        "severity": severity,
        "rule_id": violation.get("rule_id", ""),
        "category": violation.get("category", ""),
        "color": color,
        "matched_text": violation.get("matched_text", "")
    }

def get_severity_summary(violations: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get a summary count of violations by severity level.
    
    Args:
        violations (list): List of violation dictionaries
    
    Returns:
        dict: {"error": int, "warn": int, "info": int}
    """
    summary = {"error": 0, "warn": 0, "info": 0}
    
    for v in violations:
        severity = v.get("severity", "warn")
        if severity in summary:
            summary[severity] += 1
    
    return summary

def filter_violations_by_severity(violations: List[Dict[str, Any]], 
                                  severity_level: str) -> List[Dict[str, Any]]:
    """
    Filter violations to only include specified severity level.
    
    Args:
        violations (list): List of violation dictionaries
        severity_level (str): "error", "warn", or "info"
    
    Returns:
        list: Filtered violations
    """
    return [v for v in violations if v.get("severity") == severity_level]
