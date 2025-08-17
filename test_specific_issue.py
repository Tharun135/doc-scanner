#!/usr/bin/env python3
"""
Test the specific text that's being flagged for space before punctuation
"""

from app.rules.formatting_fixed import check
import re

def test_specific_text():
    text = """Prerequisite
The WinCC Unified Runtime app must be running.
A proj"""
    
    print("=== TESTING SPECIFIC TEXT ===")
    print(f"Text: '''{text}'''")
    print()
    
    # Run the formatting check
    results = check(text)
    print(f"Total formatting issues found: {len(results)}")
    print()
    
    # Filter for space before punctuation issues
    space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
    
    if space_issues:
        print("SPACE BEFORE PUNCTUATION ISSUES:")
        for i, issue in enumerate(space_issues, 1):
            print(f"{i}. Issue:")
            print(f"   Text flagged: '{issue['text']}'")
            print(f"   Message: {issue['message']}")
            print(f"   Position: {issue['start']}-{issue['end']}")
            
            # Show context around the issue
            start = max(0, issue['start'] - 10)
            end = min(len(text), issue['end'] + 10)
            context = text[start:end]
            print(f"   Context: '{context}'")
            
            # Show character analysis
            flagged_text = issue['text']
            print(f"   Character analysis:")
            for j, char in enumerate(flagged_text):
                if char == ' ':
                    print(f"     {j}: SPACE (\\s)")
                elif char in '.!?,:;':
                    print(f"     {j}: PUNCTUATION '{char}'")
                else:
                    print(f"     {j}: '{char}'")
            print()
    else:
        print("✅ NO space before punctuation issues found")
    
    # Manual regex test
    pattern = r'\s+[.!?,:;]'
    matches = list(re.finditer(pattern, text))
    
    print(f"\nMANUAL REGEX TEST:")
    print(f"Pattern: {pattern}")
    print(f"Matches found: {len(matches)}")
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. Match at position {match.start()}-{match.end()}: '{match.group()}'")
        # Show surrounding context
        start = max(0, match.start() - 10)
        end = min(len(text), match.end() + 10)
        context = text[start:end]
        print(f"   Context: '{context}'")
    
    # Check each line individually
    print(f"\nLINE-BY-LINE ANALYSIS:")
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        print(f"Line {i}: '{line}'")
        line_matches = list(re.finditer(pattern, line))
        if line_matches:
            for match in line_matches:
                print(f"  ❌ Space before punctuation: '{match.group()}' at position {match.start()}")
        else:
            print(f"  ✅ No space before punctuation issues")

if __name__ == "__main__":
    test_specific_text()
