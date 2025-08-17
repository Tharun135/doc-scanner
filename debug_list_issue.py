#!/usr/bin/env python3
"""
Debug why the list items are still being flagged
"""

from app.rules.formatting_fixed import check

def debug_list_issue():
    print("=== DEBUGGING LIST ISSUE ===\n")
    
    # Test with your exact example
    test_texts = [
        # Original text as you provided
        """Prerequisite
The WinCC Unified Runtime app must be running.
A project must be added as described in Add Project.""",
        
        # Possible variations that might be causing the issue
        """Prerequisite:
- The WinCC Unified Runtime app must be running.
- A project must be added as described in Add Project.""",
        
        # With spaces before periods
        """Prerequisite:
- The WinCC Unified Runtime app must be running .
- A project must be added as described in Add Project .""",
        
        # Test individual sentences
        "The WinCC Unified Runtime app must be running.",
        "A project must be added as described in Add Project.",
        "The WinCC Unified Runtime app must be running .",
        "A project must be added as described in Add Project .",
        
        # Test list format with spaces
        "- The WinCC Unified Runtime app must be running .",
        "- A project must be added as described in Add Project .",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"TEST {i}:")
        print(f"Text: {repr(text)}")
        print("Rendered:")
        print(text)
        print()
        
        results = check(text)
        punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"❌ FLAGGED: {len(punctuation_issues)} punctuation issues")
            for j, issue in enumerate(punctuation_issues, 1):
                print(f"   {j}. '{issue['text']}' at position {issue['start']}-{issue['end']}")
                # Show context
                start = max(0, issue['start'] - 10)
                end = min(len(text), issue['end'] + 10)
                context = text[start:end]
                print(f"      Context: {repr(context)}")
        else:
            print("✅ NOT FLAGGED")
        
        print("-" * 60)

def check_list_detection():
    print("\n=== CHECKING LIST DETECTION LOGIC ===\n")
    
    import re
    
    test_lines = [
        "The WinCC Unified Runtime app must be running.",
        "A project must be added as described in Add Project.",
        "- The WinCC Unified Runtime app must be running.",
        "- A project must be added as described in Add Project.",
        "• The WinCC Unified Runtime app must be running.",
        "* A project must be added as described in Add Project.",
        "1. The WinCC Unified Runtime app must be running.",
        "2. A project must be added as described in Add Project.",
    ]
    
    bullet_pattern = r'^\s*[-*•·]\s'
    number_pattern = r'^\s*\d+\.\s'
    
    for line in test_lines:
        is_bullet = bool(re.match(bullet_pattern, line))
        is_number = bool(re.match(number_pattern, line))
        is_list_line = is_bullet or is_number
        
        print(f"Line: {repr(line)}")
        print(f"  Bullet match: {is_bullet}")
        print(f"  Number match: {is_number}")
        print(f"  Is list line: {is_list_line}")
        print()

if __name__ == "__main__":
    debug_list_issue()
    check_list_detection()
