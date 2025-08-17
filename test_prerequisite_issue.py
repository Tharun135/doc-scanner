#!/usr/bin/env python3
"""
Test why the prerequisite text is being flagged for space before punctuation
"""

from app.rules.formatting_fixed import check
import re

def test_prerequisite_text():
    # The exact text you provided
    text = """Prerequisite
The WinCC Unified Runtime app must be running.
A project must be added as described in Add Project."""
    
    print("=== TESTING PREREQUISITE TEXT ===\n")
    print("RAW TEXT REPRESENTATION:")
    print(repr(text))
    print("\nFORMATTED TEXT:")
    print(text)
    print("\n" + "="*60 + "\n")
    
    # Test with formatting rules
    results = check(text)
    
    print(f"TOTAL FORMATTING ISSUES FOUND: {len(results)}\n")
    
    space_before_punct_issues = []
    other_issues = []
    
    for result in results:
        if "space before punctuation" in result.get('message', '').lower():
            space_before_punct_issues.append(result)
        else:
            other_issues.append(result)
    
    # Show space before punctuation issues specifically
    if space_before_punct_issues:
        print("🚨 SPACE BEFORE PUNCTUATION ISSUES:")
        for i, issue in enumerate(space_before_punct_issues, 1):
            print(f"\n{i}. {issue.get('message', 'N/A')}")
            print(f"   Flagged text: '{issue.get('text', 'N/A')}'")
            print(f"   Position: {issue.get('start', 'N/A')}-{issue.get('end', 'N/A')}")
            
            # Show detailed context
            start = issue.get('start', 0)
            end = issue.get('end', 0)
            
            # Get characters around the issue
            before_start = max(0, start - 20)
            after_end = min(len(text), end + 20)
            context = text[before_start:after_end]
            
            print(f"   Context: '{context}'")
            
            # Show exactly what character is flagged
            if start > 0:
                char_before = repr(text[start-1])
                char_at_start = repr(text[start]) if start < len(text) else 'EOF'
                char_at_end = repr(text[end-1]) if end > 0 and end <= len(text) else 'N/A'
                
                print(f"   Character before issue: {char_before}")
                print(f"   Character at start: {char_at_start}")
                print(f"   Character at end: {char_at_end}")
    else:
        print("✅ NO SPACE BEFORE PUNCTUATION ISSUES FOUND")
    
    # Show other issues
    if other_issues:
        print(f"\n📋 OTHER FORMATTING ISSUES ({len(other_issues)}):")
        for i, issue in enumerate(other_issues, 1):
            print(f"\n{i}. {issue.get('message', 'N/A')}")
            print(f"   Text: '{issue.get('text', 'N/A')}'")
    
    # Manual regex analysis
    print(f"\n" + "="*60)
    print("MANUAL REGEX ANALYSIS")
    print("="*60)
    
    # The exact pattern from formatting_fixed.py
    pattern = r'\s+[.!?,:;]'
    print(f"\nPattern: {pattern}")
    print("Explanation: One or more whitespace characters followed by punctuation")
    
    matches = list(re.finditer(pattern, text))
    print(f"Matches found: {len(matches)}\n")
    
    if matches:
        for i, match in enumerate(matches, 1):
            matched_text = match.group()
            start_pos = match.start()
            end_pos = match.end()
            
            print(f"Match {i}:")
            print(f"  Matched: {repr(matched_text)} (positions {start_pos}-{end_pos})")
            
            # Show what type of whitespace
            whitespace_chars = matched_text[:-1]  # All except the punctuation
            punctuation_char = matched_text[-1]   # The punctuation
            
            print(f"  Whitespace: {repr(whitespace_chars)} (length: {len(whitespace_chars)})")
            print(f"  Punctuation: {repr(punctuation_char)}")
            
            # Show context
            context_start = max(0, start_pos - 15)
            context_end = min(len(text), end_pos + 15)
            context = text[context_start:context_end]
            print(f"  Context: {repr(context)}")
            
            # Check if it's a line break
            if '\n' in whitespace_chars:
                print(f"  ⚠️  Contains line break - this might be a false positive for list formatting")
            
            print()
    
    # Check each line individually
    print("LINE-BY-LINE ANALYSIS:")
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        print(f"\nLine {i}: {repr(line)}")
        line_matches = list(re.finditer(pattern, line))
        if line_matches:
            print(f"  🚨 Contains space before punctuation:")
            for match in line_matches:
                print(f"    {repr(match.group())} at position {match.start()}-{match.end()}")
        else:
            print(f"  ✅ No space before punctuation")

if __name__ == "__main__":
    test_prerequisite_text()
