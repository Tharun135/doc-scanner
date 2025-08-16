"""
Capitalization Rules - Compatible with App Structure
Detects capitalization issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for capitalization issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Product names that should be capitalized (case-insensitive search)
    product_names = [
        'microsoft', 'windows', 'office', 'excel', 'word', 'powerpoint', 
        'outlook', 'teams', 'azure', 'github', 'google', 'apple', 'amazon',
        'oracle', 'ibm', 'intel', 'nvidia', 'amd', 'docker', 'kubernetes',
        'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue'
    ]
    
    # Check for improperly capitalized product names
    for name in product_names:
        pattern = r'\b' + re.escape(name) + r'\b'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            matched_text = match.group(0)
            # Only flag if not properly capitalized
            if matched_text.lower() == name and matched_text != name.title():
                issues.append({
                    "text": matched_text,
                    "start": match.start(),
                    "end": match.end(),
                    "message": f"Capitalization issue: '{matched_text}' should be '{name.title()}'"
                })
    
    # Check for acronyms that should be uppercase
    acronyms = ['api', 'url', 'http', 'https', 'ssl', 'tls', 'vpn', 'lan', 'wan', 
                'wifi', 'usb', 'cpu', 'gpu', 'ram', 'ssd', 'hdd', 'bios', 'os', 
                'ui', 'ux', 'cli', 'gui', 'ide', 'sdk', 'rest', 'json', 'xml', 
                'html', 'css', 'sql', 'aws', 'gcp', 'git', 'mvc', 'orm', 'oop']
    
    for acronym in acronyms:
        pattern = r'\b' + re.escape(acronym) + r'\b'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            matched_text = match.group(0)
            # Only flag if not uppercase
            if matched_text.lower() == acronym and matched_text != acronym.upper():
                issues.append({
                    "text": matched_text,
                    "start": match.start(),
                    "end": match.end(),
                    "message": f"Capitalization issue: '{matched_text}' should be '{acronym.upper()}'"
                })
    
    # Check for sentences starting with lowercase letters
    sentence_pattern = r'(?:^|[.!?]\s+)([a-z])'
    for match in re.finditer(sentence_pattern, content, re.MULTILINE):
        issues.append({
            "text": match.group(1),
            "start": match.start(1),
            "end": match.end(1),
            "message": "Capitalization issue: Sentence should start with capital letter"
        })
    
    return issues
