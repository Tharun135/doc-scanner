"""
Tone Rules - Compatible with App Structure
Detects tone issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for tone issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Define tone patterns
    tone_patterns = [
        # Overly casual language
        {
            'pattern': r'\b(?:gonna|wanna|gotta|kinda|sorta|dunno|yeah|nah|ok|cool|awesome|super|totally)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Casual language - consider more formal alternatives for professional writing'
        },
        # Overly aggressive language
        {
            'pattern': r'\b(?:obviously|clearly|definitely|absolutely|never|always|impossible|ridiculous|stupid|idiotic)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Overly assertive language - consider softer alternatives'
        },
        # Hedge words (excessive)
        {
            'pattern': r'\b(?:perhaps|maybe|possibly|probably|might|could|seem|appear|tend to|sort of|kind of)\s+(?:perhaps|maybe|possibly|probably|might|could|seem|appear|tend to|sort of|kind of)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Excessive hedging weakens your message'
        },
        # Apologetic language
        {
            'pattern': r'\b(?:sorry|apologize)\s+(?:for|about|that)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Unnecessary apology in professional writing'
        },
        # Demanding language
        {
            'pattern': r'\b(?:you must|you need to|you have to|you should|you will)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Demanding tone - consider more collaborative language'
        },
        # Condescending language
        {
            'pattern': r'\b(?:as you know|of course|naturally|needless to say|it goes without saying)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Potentially condescending phrase'
        },
        # Emotional language
        {
            'pattern': r'\b(?:furious|outraged|devastated|thrilled|ecstatic|horrible|terrible|awful|amazing|incredible|unbelievable)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Highly emotional language - consider more neutral alternatives'
        },
        # Absolute statements
        {
            'pattern': r'\b(?:all|every|none|nobody|everybody|always|never)\s+[a-zA-Z]+(?:\s+[a-zA-Z]+)*\s+(?:are|is|will|would|can|cannot|must|should)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Absolute statement - consider qualifying with "most", "many", "some"'
        },
        # Blame language
        {
            'pattern': r'\b(?:your fault|you failed|you forgot|you didn\'t|you ignored|you overlooked)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Blame language - consider more constructive phrasing'
        },
        # Sarcasm indicators
        {
            'pattern': r'\b(?:great job|well done|brilliant|perfect)\s*[.!]*\s*(?:not|now|but|however)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Potential sarcasm detected - ensure tone is appropriate'
        },
        # Dismissive language
        {
            'pattern': r'\b(?:just|simply|merely|only|obviously|clearly|plainly)\s+(?:do|use|follow|implement|apply|execute)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Potentially dismissive language - what seems simple to you may not be to others'
        },
        # Gender-specific language
        {
            'pattern': r'\b(?:guys|ladies|girls|boys)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Consider gender-neutral alternatives like "team", "everyone", "colleagues"'
        },
        # Discriminatory language
        {
            'pattern': r'\b(?:normal|abnormal|weird|strange|crazy|insane|lame|dumb)\b',
            'flags': re.IGNORECASE,
            'message': 'Tone issue: Potentially discriminatory language - consider more inclusive alternatives'
        }
    ]
    
    for pattern_info in tone_patterns:
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
