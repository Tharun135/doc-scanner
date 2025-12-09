"""
Rule Loader Module
Loads atomic rule definitions from rules.json
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

_rules_cache = None

def load_rules():
    """
    Load rules from rules.json file.
    Uses caching to avoid repeated file I/O.
    
    Returns:
        list: List of rule dictionaries with structure:
              {
                "rule_id": str,
                "category": str,
                "regex": str,
                "severity": str (error|warn|info),
                "message": str,
                "suggestion": str
              }
    """
    global _rules_cache
    
    # Return cached rules if available
    if _rules_cache is not None:
        return _rules_cache
    
    # Determine path to rules.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rules_file = os.path.join(current_dir, "rules.json")
    
    try:
        with open(rules_file, "r", encoding="utf-8") as f:
            rules = json.load(f)
            _rules_cache = rules
            logger.info(f"✅ Loaded {len(rules)} atomic rules from {rules_file}")
            return rules
    except FileNotFoundError:
        logger.error(f"❌ Rules file not found: {rules_file}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in rules file: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error loading rules: {e}")
        return []

def get_rules_by_category(category):
    """
    Get all rules for a specific category.
    
    Args:
        category (str): Category name (tense, ui-label, safety, etc.)
    
    Returns:
        list: Filtered list of rules matching the category
    """
    all_rules = load_rules()
    return [rule for rule in all_rules if rule.get("category") == category]

def get_rules_by_severity(severity):
    """
    Get all rules for a specific severity level.
    
    Args:
        severity (str): Severity level (error, warn, info)
    
    Returns:
        list: Filtered list of rules matching the severity
    """
    all_rules = load_rules()
    return [rule for rule in all_rules if rule.get("severity") == severity]

def reload_rules():
    """
    Force reload of rules from disk.
    Useful for development or if rules.json is updated at runtime.
    """
    global _rules_cache
    _rules_cache = None
    return load_rules()
