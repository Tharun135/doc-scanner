#!/usr/bin/env python3
"""
Test the modified formatting rule
"""

from app.rules.formatting_fixed import check

def test_modified_rule():
    print("=== TESTING MODIFIED FORMATTING RULE ===\n")
    
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
        
        # Mixed content
        ("Introduction:\nThis is wrong . But this list is ok:\n- Item one .\n- Item two .", "Mixed content"),
    ]
    
    for text, description in test_cases:
        print(f"Testing: {description}")
        print(f"Text: {repr(text)}")
        
        results = check(text)
        punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        print(f"Total issues found: {len(results)}")
        if punctuation_issues:
            print(f"   ❌ Punctuation spacing issues: {len(punctuation_issues)}")
            for issue in punctuation_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"   ✅ No punctuation spacing issues")
        
        # Show other issues too
        other_issues = [r for r in results if "space before punctuation" not in r.get('message', '')]
        if other_issues:
            print(f"   Other formatting issues: {len(other_issues)}")
            for issue in other_issues[:2]:  # Show first 2
                print(f"      - {issue['message']}: '{issue['text']}'")
        print()

if __name__ == "__main__":
    test_modified_rule()
