#!/usr/bin/env python3
"""
Create improved formatting rule with list awareness
"""

import re
from typing import List, Dict, Any

def improved_check_formatting(content: str) -> List[Dict[str, Any]]:
    """
    Improved formatting check that allows spaces before punctuation in lists
    """
    issues = []
    
    # Split content into lines to handle list detection
    lines = content.split('\n')
    current_pos = 0
    
    for line in lines:
        # Check if this line is a list item
        is_list_line = bool(re.match(r'^\s*[-*•·]\s', line) or re.match(r'^\s*\d+\.\s', line))
        
        if not is_list_line:
            # Only check for space before punctuation in non-list lines
            for match in re.finditer(r'\s+[.!?,:;]', line):
                matched_text = match.group(0)
                issues.append({
                    "text": matched_text,
                    "start": current_pos + match.start(),
                    "end": current_pos + match.end(),
                    "message": "Formatting issue: Remove space before punctuation"
                })
        
        # Move to next line (add 1 for the newline character)
        current_pos += len(line) + 1
    
    return issues

def test_improved_function():
    print("=== TESTING IMPROVED FORMATTING FUNCTION ===\n")
    
    test_cases = [
        # Should be ALLOWED (list formatting)
        ("Prerequisite:\n- The app must be running .\n- A project must be added .", "List with dashes"),
        ("Steps:\n• First item .\n• Second item .", "List with bullets"),
        ("Notes:\n* Important point .\n* Another point .", "List with asterisks"),
        ("Items:\n1. First item .\n2. Second item .", "Numbered list"),
        ("Requirements:\n  - Indented item .\n  - Another item .", "Indented list"),
        
        # Should be FLAGGED (regular text)
        ("This is wrong . Regular text.", "Regular sentence"),
        ("Hello , world", "Regular comma spacing"),
        ("What ? This is wrong.", "Regular question"),
        ("Multiple issues : wrong , spacing .", "Multiple issues"),
    ]
    
    for text, description in test_cases:
        print(f"Testing: {description}")
        print(f"Text: {repr(text)}")
        
        results = improved_check_formatting(text)
        punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"   ❌ FLAGGED: {len(punctuation_issues)} issues")
            for issue in punctuation_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"   ✅ ALLOWED: No punctuation spacing issues")
        print()

if __name__ == "__main__":
    test_improved_function()
