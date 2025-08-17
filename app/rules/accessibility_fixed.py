"""
Accessibility Rules - Compatible with App Structure
Detects accessibility issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for accessibility issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Define accessibility patterns
    accessibility_patterns = [
        # Color-only references
        {
            'pattern': r'\b(?:click the red|click the green|click the blue|see the red|see the green|see the blue|red button|green button|blue button)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Avoid color-only references - include additional descriptors'
        },
        # Directional references without context
        {
            'pattern': r'\b(?:click here|above|below|left|right|top|bottom)\s+(?:link|button|image|text)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Directional references may not be accessible - provide descriptive text'
        },
        # Sensory language without alternatives
        {
            'pattern': r'\b(?:see|look|view|watch|observe|notice|hear|listen|sound)\s+(?:the|this|that)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Sensory language - consider alternatives for non-visual users'
        },
        # Ableist language
        {
            'pattern': r'\b(?:blind to|deaf to|dumb|lame|crippled|handicapped|retarded|insane|crazy|psycho|schizo)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Ableist language - use person-first or neutral language'
        },
        # Missing alt text indicators
        {
            'pattern': r'\b(?:image|picture|photo|graphic|chart|diagram|figure)\s+(?:shows|displays|depicts)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Ensure images have descriptive alt text'
        },
        # Table references without structure
        {
            'pattern': r'\b(?:table|row|column|cell)\s+\d+\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Use proper table headers and structure for screen readers'
        },
        # Audio/video without alternatives
        {
            'pattern': r'\b(?:video|audio|sound|music|voice|recording)\s+(?:explains|shows|demonstrates)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Ensure audio/video content has captions or transcripts'
        },
        # Complex instructions without step-by-step
        {
            'pattern': r'\b(?:simply|just|quickly|easily)\s+(?:drag|drop|swipe|gesture|pinch|zoom)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Provide alternative methods for gesture-based actions'
        },
        # Time-sensitive instructions
        {
            'pattern': r'\b(?:quickly|immediately|fast|hurry|rush|before it disappears)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Avoid time pressure - allow users to work at their own pace'
        },
        # Cognitive load issues
        {
            'pattern': r'\b(?:remember|memorize|keep in mind|don\'t forget)\s+(?:to|that)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Avoid relying on memory - provide visible reminders'
        },
        # Mouse-only instructions
        {
            'pattern': r'\b(?:right-click|double-click|mouse over|hover|drag)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Provide keyboard alternatives to mouse actions'
        },
        # Unclear focus indicators
        {
            'pattern': r'\b(?:selected|active|current|focused)\s+(?:item|element|field)\b',
            'flags': re.IGNORECASE,
            'message': 'Accessibility issue: Ensure focus indicators are clearly visible'
        },
    ]
    
    for pattern_info in accessibility_patterns:
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
