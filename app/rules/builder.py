"""
Rule Builder Module
Create custom rules via structured interface.
"""

class RuleBuilder:
    """Helper class to build and validate rule definitions."""
    
    @staticmethod
    def create_rule(rule_id, category, pattern, severity, message, suggestion, 
                   example_violation="", example_correction=""):
        """
        Create a new rule definition with validation.
        
        Args:
            rule_id (str): Unique identifier (e.g., CUSTOM_001)
            category (str): Category name (e.g., custom, tense, ui-label)
            pattern (str): Regex pattern for matching
            severity (str): error, warn, or info
            message (str): Violation description
            suggestion (str): How to fix
            example_violation (str): Optional bad example
            example_correction (str): Optional good example
        
        Returns:
            dict: Rule definition ready for rules.json
        
        Raises:
            ValueError: If validation fails
        """
        # Validate severity
        if severity not in ["error", "warn", "info"]:
            raise ValueError(f"Invalid severity: {severity}. Must be error, warn, or info.")
        
        # Validate rule_id format
        if not rule_id or not rule_id[0].isupper():
            raise ValueError("Rule ID must start with uppercase letter")
        
        # Validate regex pattern
        import re
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        rule = {
            "rule_id": rule_id,
            "category": category,
            "regex": pattern,
            "severity": severity,
            "message": message,
            "suggestion": suggestion
        }
        
        if example_violation:
            rule["example_violation"] = example_violation
        if example_correction:
            rule["example_correction"] = example_correction
        
        return rule
    
    @staticmethod
    def validate_rule(rule):
        """Validate a rule definition."""
        required_fields = ["rule_id", "category", "regex", "severity", "message", "suggestion"]
        
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Missing required field: {field}")
        
        if rule["severity"] not in ["error", "warn", "info"]:
            raise ValueError(f"Invalid severity: {rule['severity']}")
        
        # Test regex
        import re
        try:
            re.compile(rule["regex"])
        except re.error as e:
            raise ValueError(f"Invalid regex: {e}")
        
        return True


# Example usage templates
RULE_TEMPLATES = {
    "ui_label": {
        "category": "ui-label",
        "severity": "error",
        "pattern_template": "\\b(?:click|select|press)\\s+(?:the|a)\\s+{LABEL}\\s+button\\b",
        "message_template": "Do not use articles or 'button' with {ELEMENT} labels.",
        "suggestion": "Use: Click <LABEL> (without 'the' or 'button')."
    },
    "terminology": {
        "category": "terminology",
        "severity": "warn",
        "pattern_template": "\\b{TERM}\\b",
        "message_template": "Inconsistent terminology: '{TERM}' should be '{PREFERRED}'.",
        "suggestion": "Use '{PREFERRED}' consistently throughout the document."
    },
    "blacklist_word": {
        "category": "clarity",
        "severity": "warn",
        "pattern_template": "\\b{WORD}\\b",
        "message_template": "Avoid using '{WORD}' - it reduces precision.",
        "suggestion": "Replace with more specific wording."
    }
}
