"""
Punctuation Rules - Compatible with App Structure
Detects punctuation issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for punctuation issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Define punctuation patterns
    punctuation_patterns = [
        # Missing periods at end of sentences
        {
            'pattern': r'[a-zA-Z][^.!?]*$',
            'flags': re.MULTILINE,
            'message': 'Punctuation issue: Sentence may be missing ending punctuation'
        },
        # Double punctuation
        {
            'pattern': r'[.!?]{2,}',
            'flags': 0,
            'message': 'Punctuation issue: Multiple ending punctuation marks'
        },
        {
            'pattern': r',,+',
            'flags': 0,
            'message': 'Punctuation issue: Multiple consecutive commas'
        },
        # Incorrect comma usage
        {
            'pattern': r'\b(?:and|or|but),\s+',
            'flags': re.IGNORECASE,
            'message': 'Punctuation issue: Remove comma before coordinating conjunctions in simple sentences'
        },
        # Missing comma in lists
        {
            'pattern': r'\b[a-zA-Z]+\s+[a-zA-Z]+\s+and\s+[a-zA-Z]+\b',
            'flags': 0,
            'message': 'Punctuation issue: Consider adding comma in series (Oxford comma)'
        },
        # Incorrect apostrophe usage
        {
            'pattern': r'\b[a-zA-Z]+s\'\s+[a-zA-Z]',
            'flags': 0,
            'message': 'Punctuation issue: Check apostrophe placement for plural possessives'
        },
        {
            'pattern': r'\b(?:its\'|yours\'|theirs\'|ours\')\b',
            'flags': re.IGNORECASE,
            'message': 'Punctuation issue: Possessive pronouns do not use apostrophes'
        },
        # Semicolon misuse
        {
            'pattern': r';\s*[A-Z]',
            'flags': 0,
            'message': 'Punctuation issue: Lowercase letter should follow semicolon unless starting proper noun'
        },
        # Colon misuse
        {
            'pattern': r':\s*[a-z]',
            'flags': 0,
            'message': 'Punctuation issue: Consider capitalizing after colon for complete sentences'
        },
        # Question mark misuse
        {
            'pattern': r'\b(?:please|kindly)\s+[^?]*\?',
            'flags': re.IGNORECASE,
            'message': 'Punctuation issue: Polite requests typically end with periods, not question marks'
        },
        # Exclamation mark overuse
        {
            'pattern': r'!.*!',
            'flags': 0,
            'message': 'Punctuation issue: Multiple exclamation marks in close proximity'
        },
        # Missing hyphens in compound adjectives
        {
            'pattern': r'\b(?:well|self|cross|re|pre|post|non|anti|multi|over|under|out)\s+[a-zA-Z]+ed?\b',
            'flags': re.IGNORECASE,
            'message': 'Punctuation issue: Consider hyphenating compound adjectives'
        },
        # Parentheses issues
        {
            'pattern': r'\([^)]*$',
            'flags': re.MULTILINE,
            'message': 'Punctuation issue: Unclosed parenthesis'
        },
        {
            'pattern': r'^[^(]*\)',
            'flags': re.MULTILINE,
            'message': 'Punctuation issue: Closing parenthesis without opening'
        }
    ]
    
    for pattern_info in punctuation_patterns:
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
