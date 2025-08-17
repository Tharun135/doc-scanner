#!/usr/bin/env python3
"""
Test and demonstrate the "Remove space before punctuation" formatting issue
"""

from app.rules.formatting_fixed import check
import re

def test_space_before_punctuation():
    print("=== FORMATTING ISSUE: Remove space before punctuation ===\n")
    
    # The actual regex pattern from formatting_fixed.py
    pattern = r'\s+[.!?,:;]'
    
    print("REGEX PATTERN:", pattern)
    print("EXPLANATION: Detects one or more spaces (\\s+) followed by punctuation [.!?,:;]\n")
    
    # Test cases - correct vs incorrect
    test_cases = [
        # INCORRECT (will be flagged)
        ("This is wrong .", "Period with space before"),
        ("Hello , world", "Comma with space before"), 
        ("What ?", "Question mark with space before"),
        ("Help !", "Exclamation with space before"),
        ("Item 1 ; Item 2", "Semicolon with space before"),
        ("Dear Sir :", "Colon with space before"),
        
        # CORRECT (will NOT be flagged)
        ("This is correct.", "Period without space before"),
        ("Hello, world", "Comma without space before"),
        ("What?", "Question mark without space before"),
        ("Help!", "Exclamation without space before"),
        ("Item 1; Item 2", "Semicolon without space before"),
        ("Dear Sir:", "Colon without space before"),
    ]
    
    print("TEST CASES:\n")
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"{i:2d}. {description}")
        print(f"    Text: '{text}'")
        
        # Test with regex
        match = re.search(pattern, text)
        if match:
            print(f"    ❌ FLAGGED: Space before '{match.group().strip()}' at position {match.start()}-{match.end()}")
        else:
            print(f"    ✅ CORRECT: No space before punctuation")
        
        # Test with actual rule
        results = check(text)
        space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        if space_issues:
            for issue in space_issues:
                print(f"    🔍 DETECTED: '{issue['text']}' - {issue['message']}")
        
        print()

def show_common_examples():
    print("\n=== COMMON EXAMPLES ===\n")
    
    examples = [
        {
            "wrong": "The meeting is at 3 PM .",
            "right": "The meeting is at 3 PM.",
            "explanation": "No space before period"
        },
        {
            "wrong": "Please review the document , make changes , and send it back .",
            "right": "Please review the document, make changes, and send it back.",
            "explanation": "No spaces before commas or period"
        },
        {
            "wrong": "What time is it ?",
            "right": "What time is it?",
            "explanation": "No space before question mark"
        },
        {
            "wrong": "Great job !",
            "right": "Great job!",
            "explanation": "No space before exclamation mark"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['explanation']}")
        print(f"   ❌ Wrong: '{example['wrong']}'")
        print(f"   ✅ Right: '{example['right']}'")
        print()

if __name__ == "__main__":
    test_space_before_punctuation()
    show_common_examples()
