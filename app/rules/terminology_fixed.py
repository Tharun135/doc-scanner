"""
Terminology Rules - Compatible with App Structure
Detects terminology issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for terminology issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Define terminology patterns with corrections
    terminology_patterns = [
        # Product name variations
        {
            'pattern': r'\b(?:ms|micro soft|micro-soft)\b',
            'correct': 'Microsoft',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "Microsoft" instead'
        },
        {
            'pattern': r'\bwin(?:dows)?\s*(?:10|11|xp|vista|7|8)\b',
            'correct': 'Windows',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use full "Windows" product name'
        },
        # Technical terminology
        {
            'pattern': r'\b(?:web site|web-site)\b',
            'correct': 'website',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "website" as one word'
        },
        {
            'pattern': r'\b(?:e-mail|e mail)\b',
            'correct': 'email',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "email" as one word'
        },
        {
            'pattern': r'\b(?:log in|log-in)\b(?!\s+(?:page|form|screen|button))',
            'correct': 'log in',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "log in" as verb, "login" as noun'
        },
        {
            'pattern': r'\b(?:sign up|sign-up)\b(?!\s+(?:page|form|screen|button))',
            'correct': 'sign up',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "sign up" as verb, "signup" as noun'
        },
        # Common technical terms
        {
            'pattern': r'\b(?:data base|data-base)\b',
            'correct': 'database',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "database" as one word'
        },
        {
            'pattern': r'\b(?:file name|file-name)\b',
            'correct': 'filename',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "filename" as one word'
        },
        {
            'pattern': r'\b(?:user name|user-name)\b',
            'correct': 'username',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "username" as one word'
        },
        # Brand and product consistency
        {
            'pattern': r'\b(?:github|git hub|git-hub)\b',
            'correct': 'GitHub',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "GitHub" with proper capitalization'
        },
        {
            'pattern': r'\b(?:javascript|java script|java-script)\b',
            'correct': 'JavaScript',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Use "JavaScript" with proper capitalization'
        },
        # Inconsistent abbreviations
        {
            'pattern': r'\b(?:app|application)\b',
            'correct': 'application',
            'flags': re.IGNORECASE,
            'message': 'Terminology issue: Be consistent with "app" vs "application"'
        },
    ]
    
    for pattern_info in terminology_patterns:
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
