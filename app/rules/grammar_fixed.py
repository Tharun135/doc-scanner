"""
Grammar Rules - Compatible with App Structure
Detects grammar issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for grammar issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Define grammar patterns
    grammar_patterns = [
        # Subject-verb agreement
        {
            'pattern': r'\b(?:this|that)\s+(?:are|were)\b',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Use "this is" or "that was" for singular subjects'
        },
        {
            'pattern': r'\b(?:these|those)\s+(?:is|was)\b',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Use "these are" or "those were" for plural subjects'
        },
        # Common verb errors
        {
            'pattern': r'\b(?:could of|would of|should of)\b',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Use "could have", "would have", or "should have"'
        },
        # Article usage
        {
            'pattern': r'\ba\s+(?:[aeiou])',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Use "an" before vowel sounds'
        },
        # Double negatives
        {
            'pattern': r'\b(?:don\'t|doesn\'t|didn\'t|won\'t|wouldn\'t|can\'t|couldn\'t)\s+(?:never|nobody|nothing|nowhere|none)\b',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Avoid double negatives'
        },
        # Incomplete comparisons
        {
            'pattern': r'\b(?:more|less)\s+(?:better|worse|easier|harder)\b',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Avoid redundant comparisons'
        },
        # Comma splices (basic detection)
        {
            'pattern': r'\b[a-zA-Z]+,\s+(?:however|therefore|thus|consequently|furthermore|moreover|nevertheless)\s+[a-z]',
            'flags': 0,
            'message': 'Grammar issue: Consider using semicolon before transitional words'
        },
        # Misplaced apostrophes
        {
            'pattern': r'\b(?:it\'s)\s+(?:own|color|size|shape|purpose)\b',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Use "its" (possessive) not "it\'s" (contraction)'
        },
        # Split infinitives (conservative approach)
        {
            'pattern': r'\bto\s+(?:really|quickly|completely|totally|actually|finally|properly)\s+(?:understand|complete|implement|configure|install|setup|create|develop)\b',
            'flags': re.IGNORECASE,
            'message': 'Grammar issue: Consider avoiding split infinitives in formal writing'
        }
    ]
    
    for pattern_info in grammar_patterns:
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
