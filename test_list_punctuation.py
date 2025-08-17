#!/usr/bin/env python3
"""
Test current behavior and create improved rule for list punctuation
"""

import re
from app.rules.formatting_fixed import check

def test_current_behavior():
    print("=== TESTING CURRENT BEHAVIOR ===\n")
    
    # Test cases that should be allowed (list formatting)
    list_cases = [
        "Prerequisite:\n- The app must be running .\n- A project must be added .",
        "Steps:\n1. Open the file .\n2. Save the changes .",
        "Requirements:\n• First item .\n• Second item .",
        "Notes:\n* Important point .\n* Another point .",
    ]
    
    # Test cases that should still be flagged (regular text)
    regular_cases = [
        "This is wrong . Regular sentence with space before period.",
        "Hello , world",
        "What ? This should be flagged.",
    ]
    
    print("LIST CASES (should potentially be allowed):")
    for i, text in enumerate(list_cases, 1):
        print(f"\n{i}. Text: {repr(text)}")
        results = check(text)
        punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        if punctuation_issues:
            print(f"   ❌ FLAGGED: {len(punctuation_issues)} issues")
            for issue in punctuation_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"   ✅ NOT FLAGGED")
    
    print("\n" + "="*50)
    print("REGULAR CASES (should still be flagged):")
    for i, text in enumerate(regular_cases, 1):
        print(f"\n{i}. Text: {repr(text)}")
        results = check(text)
        punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        if punctuation_issues:
            print(f"   ✅ CORRECTLY FLAGGED: {len(punctuation_issues)} issues")
            for issue in punctuation_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"   ❌ NOT FLAGGED (should be flagged)")

def design_improved_pattern():
    print("\n=== DESIGNING IMPROVED PATTERN ===\n")
    
    # Current pattern
    current_pattern = r'\s+[.!?,:;]'
    print(f"Current pattern: {current_pattern}")
    print("Issue: Flags ALL spaces before punctuation")
    
    # Improved pattern - exclude list contexts
    # Look for spaces before punctuation that are NOT in list contexts
    improved_pattern = r'(?<!^[\s]*[-*•·]\s[^.\n]*)\s+[.!?,:;](?!\s*$)'
    
    print(f"\nImproved pattern: {improved_pattern}")
    print("Explanation:")
    print("- (?<!^[\\s]*[-*•·]\\s[^.\\n]*) = Negative lookbehind: NOT preceded by list bullet")
    print("- \\s+[.!?,:;] = One or more spaces before punctuation")
    print("- (?!\\s*$) = Negative lookahead: NOT followed by end of line")
    
    # Alternative simpler approach
    simpler_pattern = r'(?<![•\-*])\s+[.!?,:;]'
    print(f"\nSimpler alternative: {simpler_pattern}")
    print("- (?<![•\\-*]) = NOT preceded by bullet characters")
    print("- \\s+[.!?,:;] = spaces before punctuation")

if __name__ == "__main__":
    test_current_behavior()
    design_improved_pattern()
