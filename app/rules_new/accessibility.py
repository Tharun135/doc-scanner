"""
Accessibility and Inclusivity Rules
Ensures content is accessible and uses inclusive language.
"""

import re
import logging
from typing import List, Dict, Any

# Import the AI helper
try:
    from .llamaindex_helper import get_ai_suggestion, is_ai_available
except ImportError:
    def get_ai_suggestion(issue_text, sentence_context, category="accessibility"):
        return {"suggestion": f"Accessibility issue: {issue_text}", "confidence": 0.5}
    def is_ai_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for accessibility and inclusivity issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # 1. Alt text issues
    alt_text_issues = _check_alt_text(content)
    for issue in alt_text_issues:
        ai_response = get_ai_suggestion(
            issue_text="Missing or poor alt text",
            sentence_context=issue,
            category="accessibility"
        )
        suggestions.append(ai_response.get("suggestion", issue))
    
    # 2. Color contrast and visual accessibility
    color_issues = _check_color_accessibility(content)
    for issue in color_issues:
        ai_response = get_ai_suggestion(
            issue_text="Color accessibility concern",
            sentence_context=issue,
            category="accessibility"
        )
        suggestions.append(ai_response.get("suggestion", issue))
    
    # 3. Link accessibility
    link_issues = _check_link_accessibility(content)
    for issue in link_issues:
        ai_response = get_ai_suggestion(
            issue_text="Link accessibility issue",
            sentence_context=issue,
            category="accessibility"
        )
        suggestions.append(ai_response.get("suggestion", issue))
    
    # 4. Inclusive language
    inclusive_issues = _check_inclusive_language(content)
    for issue in inclusive_issues:
        ai_response = get_ai_suggestion(
            issue_text="Non-inclusive language detected",
            sentence_context=issue,
            category="accessibility"
        )
        suggestions.append(ai_response.get("suggestion", issue))
    
    # 5. Screen reader compatibility
    screen_reader_issues = _check_screen_reader_compatibility(content)
    for issue in screen_reader_issues:
        ai_response = get_ai_suggestion(
            issue_text="Screen reader compatibility issue",
            sentence_context=issue,
            category="accessibility"
        )
        suggestions.append(ai_response.get("suggestion", issue))
    
    return suggestions

def _check_alt_text(content: str) -> List[str]:
    """Check for missing or poor alt text."""
    issues = []
    
    # Check for images without alt text
    img_without_alt = re.findall(r'<img[^>]*(?!alt=)[^>]*>', content, re.IGNORECASE)
    for img in img_without_alt:
        issues.append(f"Image missing alt text: {img}")
    
    # Check for poor alt text
    poor_alt_patterns = [
        r'alt=["\']image["\']',
        r'alt=["\']picture["\']',
        r'alt=["\']photo["\']',
        r'alt=["\']["\']',  # empty alt text
    ]
    
    for pattern in poor_alt_patterns:
        matches = re.findall(f'<img[^>]*{pattern}[^>]*>', content, re.IGNORECASE)
        for match in matches:
            issues.append(f"Poor alt text detected: {match}")
    
    return issues

def _check_color_accessibility(content: str) -> List[str]:
    """Check for color accessibility issues."""
    issues = []
    
    # Look for color-only instructions
    color_only_patterns = [
        r'\b(click|press|select)\s+the\s+(red|green|blue|yellow|orange|purple)\b',
        r'\b(red|green|blue|yellow|orange|purple)\s+(button|link|text)\b',
        r'\bsee\s+the\s+(red|green|blue|yellow|orange|purple)\b'
    ]
    
    for pattern in color_only_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append(f"Color-only instruction: '{match.group()}'")
    
    return issues

def _check_link_accessibility(content: str) -> List[str]:
    """Check for link accessibility issues."""
    issues = []
    
    # Check for poor link text
    poor_link_patterns = [
        r'<a[^>]*>click here</a>',
        r'<a[^>]*>here</a>',
        r'<a[^>]*>this</a>',
        r'<a[^>]*>link</a>',
        r'<a[^>]*>read more</a>',
        r'<a[^>]*>more</a>'
    ]
    
    for pattern in poor_link_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append(f"Non-descriptive link text: {match.group()}")
    
    return issues

def _check_inclusive_language(content: str) -> List[str]:
    """Check for non-inclusive language."""
    issues = []
    
    # Non-inclusive terms and better alternatives
    non_inclusive_terms = {
        r'\bblacklist\b': 'blocklist',
        r'\bwhitelist\b': 'allowlist',
        r'\bmaster\b': 'main/primary',
        r'\bslave\b': 'secondary/worker',
        r'\bguys\b': 'everyone/folks/team',
        r'\bmankind\b': 'humanity/people',
        r'\bmanmade\b': 'artificial/synthetic',
        r'\bmanpower\b': 'workforce/personnel',
        r'\bchairman\b': 'chairperson/chair',
        r'\bfireman\b': 'firefighter',
        r'\bmailman\b': 'mail carrier',
        r'\bpoliceman\b': 'police officer',
        r'\bcrazy\b': 'unexpected/surprising',
        r'\binsane\b': 'extreme/intense',
        r'\bdumb\b': 'unclear/confusing',
        r'\blame\b': 'ineffective/poor'
    }
    
    for pattern, alternative in non_inclusive_terms.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append(f"Non-inclusive language: '{match.group()}' - consider '{alternative}'")
    
    return issues

def _check_screen_reader_compatibility(content: str) -> List[str]:
    """Check for screen reader compatibility issues."""
    issues = []
    
    # Check for missing heading structure
    if '<h1' in content.lower():
        h1_count = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
        if h1_count > 1:
            issues.append("Multiple H1 headings detected - use only one H1 per page")
    
    # Check for skipped heading levels
    headings = re.findall(r'<h([1-6])[^>]*>', content, re.IGNORECASE)
    if headings:
        heading_levels = [int(h) for h in headings]
        for i in range(1, len(heading_levels)):
            if heading_levels[i] - heading_levels[i-1] > 1:
                issues.append("Skipped heading level detected - maintain proper heading hierarchy")
                break
    
    # Check for tables without headers
    table_pattern = r'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, content, re.IGNORECASE | re.DOTALL)
    for table in tables:
        if '<th' not in table.lower():
            issues.append("Table without header cells (th) detected")
    
    return issues
