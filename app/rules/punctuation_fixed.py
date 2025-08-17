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
    
    # Helper function to detect if text is likely a title/heading
    def is_likely_title(text: str) -> bool:
        """Check if text appears to be a title or heading"""
        text = text.strip()
        
        # Common title characteristics:
        # 1. Short text (typically under 100 characters)
        # 2. Doesn't contain multiple sentences
        # 3. May be title case or all caps
        # 4. Common title words
        
        if len(text) > 100:
            return False
            
        # Check for title case (most words capitalized)
        words = text.split()
        if len(words) > 1:
            capitalized_words = sum(1 for word in words if word and word[0].isupper())
            if capitalized_words >= len(words) * 0.6:  # 60% or more words capitalized
                return True
        
        # Check for common title patterns
        title_indicators = [
            'chapter', 'section', 'part', 'appendix', 'introduction', 'conclusion',
            'summary', 'overview', 'background', 'methodology', 'results', 'discussion',
            'references', 'bibliography', 'acknowledgments', 'abstract', 'table of contents'
        ]
        
        text_lower = text.lower()
        if any(indicator in text_lower for indicator in title_indicators):
            return True
            
        # Check if it's likely a heading (short and doesn't read like a sentence)
        if len(words) <= 6 and not any(word.lower() in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'] for word in words):
            return True
            
        return False
    
    # Define punctuation patterns
    punctuation_patterns = [
        # Missing periods at end of sentences (MODIFIED: exclude titles)
        {
            'pattern': r'[a-zA-Z][^.!?]*$',
            'flags': re.MULTILINE,
            'message': 'Punctuation issue: Sentence may be missing ending punctuation',
            'exclude_titles': True  # Added flag to exclude titles
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
        exclude_titles = pattern_info.get('exclude_titles', False)
        
        for match in re.finditer(pattern, content, flags):
            matched_text = match.group(0)
            
            # Skip this match if it's flagged to exclude titles and the text appears to be a title
            if exclude_titles and is_likely_title(matched_text):
                continue
                
            issues.append({
                "text": matched_text,
                "start": match.start(),
                "end": match.end(),
                "message": message
            })
    
    return issues
