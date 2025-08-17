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

    # Only check capitalization for headings (Markdown: lines starting with #, ##, etc.)
    heading_pattern = re.compile(r'^(#+)\s+(.*)$', re.MULTILINE)
    for match in heading_pattern.finditer(content):
        heading_text = match.group(2).strip()
        # Skip check if heading is empty
        if not heading_text:
            continue
        # Check if first character is lowercase (should be capitalized)
        if heading_text and heading_text[0].islower():
            issues.append({
                "text": heading_text,
                "start": match.start(2),
                "end": match.end(2),
                "message": "Formatting issue: Heading should start with a capital letter"
            })
        # Do NOT check technical terms (e.g., JSON, API, Python, etc.) in headings; allow them to start with a capital letter

    # Optionally, add HTML heading support:
    html_heading_pattern = re.compile(r'<h[1-6][^>]*>(.*?)</h[1-6]>', re.IGNORECASE)
    for match in html_heading_pattern.finditer(content):
        heading_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        if not heading_text:
            continue
        if heading_text and heading_text[0].islower():
            issues.append({
                "text": heading_text,
                "start": match.start(1),
                "end": match.end(1),
                "message": "Formatting issue: Heading should start with a capital letter"
            })

    # Never check regular sentences for heading capitalization issues
    return issues
