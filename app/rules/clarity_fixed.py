"""
Clarity Rules - Compatible with App Structure
Detects clarity issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for clarity issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Define clarity patterns
    clarity_patterns = [
        # Redundant phrases
        {
            'pattern': r'\b(?:advance planning|future plans|final outcome|end result|close proximity|exact same|free gift|past history|personal opinion|true facts|unexpected surprise|very unique)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Redundant phrase detected - consider simplifying'
        },
        # Wordy expressions
        {
            'pattern': r'\b(?:at this point in time|due to the fact that|in the event that|for the purpose of|in order to|with regard to|in terms of|on the basis of)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Wordy expression - consider more concise alternative'
        },
        # Vague pronouns
        {
            'pattern': r'\b(?:this|that|it|they)\s+(?:will|would|can|could|should|might|may)\s+[a-z]',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Vague pronoun reference - specify what "this/that/it" refers to'
        },
        # Nominalizations (turning verbs into nouns)
        {
            'pattern': r'\b(?:implementation|utilization|optimization|maximization|minimization|facilitation|coordination|standardization)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Consider using active verb form instead of nominalization'
        },
        # Weak verbs
        {
            'pattern': r'\b(?:is|are|was|were|has|have|had)\s+(?:able to|going to|planning to|trying to|working to)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Consider using stronger, more direct verbs'
        },
        # Unnecessary qualifiers
        {
            'pattern': r'\b(?:quite|rather|somewhat|fairly|pretty|very|really|actually|basically|essentially|literally)\s+(?:good|bad|important|significant|large|small|easy|difficult)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Unnecessary qualifier weakens the statement'
        },
        # Double modals
        {
            'pattern': r'\b(?:might|may|could|would|should)\s+(?:be able to|have to|need to|want to)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Avoid double modals - choose one modal verb'
        },
        # Unclear referents
        {
            'pattern': r'\b(?:the former|the latter)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: "Former/latter" can be unclear - consider restating the specific reference'
        },
        # Buried subjects
        {
            'pattern': r'^(?:There is|There are|It is|It was)\s+[^.]*\bthat\b',
            'flags': re.MULTILINE | re.IGNORECASE,
            'message': 'Clarity issue: Consider starting with the actual subject for clearer writing'
        },
        # Negative constructions
        {
            'pattern': r'\b(?:not un|not in|not dis|not im)\w+',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Double negative - consider positive phrasing'
        },
        # Long sentences (basic detection)
        {
            'pattern': r'[A-Z][^.!?]*(?:,|\s+(?:and|or|but|because|since|although|while|when|where|if))[^.!?]*(?:,|\s+(?:and|or|but|because|since|although|while|when|where|if))[^.!?]*[.!?]',
            'flags': 0,
            'message': 'Clarity issue: Long sentence with multiple clauses - consider breaking into shorter sentences'
        },
        # Jargon and buzzwords
        {
            'pattern': r'\b(?:synergy|leverage|paradigm|best practices|core competencies|low-hanging fruit|think outside the box|move the needle|circle back|touch base)\b',
            'flags': re.IGNORECASE,
            'message': 'Clarity issue: Business jargon detected - consider clearer, more specific language'
        }
    ]
    
    for pattern_info in clarity_patterns:
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
