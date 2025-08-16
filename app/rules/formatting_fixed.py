"""
Formatting Rules - Compatible with App Structure
Detects formatting issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for formatting issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Define formatting patterns
    formatting_patterns = [
        # Multiple spaces
        {
            'pattern': r'[^\s]\s{2,}[^\s]',
            'flags': 0,
            'message': 'Formatting issue: Multiple consecutive spaces detected'
        },
        # Inconsistent quote usage
        {
            'pattern': r'["""].*?["""]',
            'flags': 0,
            'message': 'Formatting issue: Use consistent quotation marks (straight quotes recommended)'
        },
        # Missing space after punctuation
        {
            'pattern': r'[.!?][a-zA-Z]',
            'flags': 0,
            'message': 'Formatting issue: Add space after punctuation'
        },
        {
            'pattern': r',[a-zA-Z]',
            'flags': 0,
            'message': 'Formatting issue: Add space after comma'
        },
        # Space before punctuation
        {
            'pattern': r'\s+[.!?,:;]',
            'flags': 0,
            'message': 'Formatting issue: Remove space before punctuation'
        },
        # Inconsistent bullet points
        {
            'pattern': r'^[\s]*[-*•·]\s*[a-zA-Z]',
            'flags': re.MULTILINE,
            'message': 'Formatting issue: Use consistent bullet point style'
        },
        # Missing spaces around operators
        {
            'pattern': r'[a-zA-Z0-9][=+\-*/][a-zA-Z0-9]',
            'flags': 0,
            'message': 'Formatting issue: Add spaces around operators'
        },
        # Inconsistent dash usage
        {
            'pattern': r'[a-zA-Z]-[a-zA-Z]',
            'flags': 0,
            'message': 'Formatting issue: Check hyphen usage in compound words'
        },
        # Multiple line breaks
        {
            'pattern': r'\n\s*\n\s*\n',
            'flags': 0,
            'message': 'Formatting issue: Excessive line breaks detected'
        },
        # Trailing whitespace
        {
            'pattern': r'[^\s]\s+$',
            'flags': re.MULTILINE,
            'message': 'Formatting issue: Trailing whitespace at end of line'
        },
        # Mixed case in headers (basic detection)
        {
            'pattern': r'^[A-Z][a-z]+\s+[a-z]+\s+[A-Z]',
            'flags': re.MULTILINE,
            'message': 'Formatting issue: Inconsistent capitalization in heading'
        },
        # Number formatting
        {
            'pattern': r'\b\d{4,}\b',
            'flags': 0,
            'message': 'Formatting issue: Consider using comma separators for large numbers'
        }
    ]
    
    for pattern_info in formatting_patterns:
        pattern = pattern_info['pattern']
        flags = pattern_info.get('flags', 0)
        message = pattern_info['message']
        
        for match in re.finditer(pattern, content, flags):
            matched_text = match.group(0)
            issues.append({
                "text": matched_text,
                "start": match.start(),
                "end": match.end(),
                "message": message
            })
    
    return issues
