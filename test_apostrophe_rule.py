#!/usr/bin/env python3
"""
Test script to verify apostrophe rule distinguishes between possessive and plural usage
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.special_characters import check

def test_apostrophe_rule():
    """Test the updated apostrophe rule"""
    
    test_cases = [
        # Possessive cases (should NOT trigger warning)
        "Tharun's laptop is on the desk.",
        "The company's policy has changed.",
        "Sarah's book is interesting.",
        "The dog's tail is wagging.",
        
        # Contractions (should NOT trigger warning)
        "It's raining outside.",
        "He's coming to the meeting.",
        "What's the time?",
        
        # Potential plural misuse (should trigger warning)
        "The CPU's are overheating.",  # Should be "CPUs"
        "Download the PDF's here.",     # Should be "PDFs"
        "All the API's are working.",   # Should be "APIs"
        
        # Mixed cases
        "John's computer and the server's are both running the latest software updates.",
    ]
    
    print("Testing apostrophe rule for possessive vs plural usage:")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        suggestions = check(test_case)
        
        apostrophe_suggestions = [s for s in suggestions if "apostrophe" in s.lower()]
        
        if apostrophe_suggestions:
            print(f"  ⚠️  Suggestions ({len(apostrophe_suggestions)}):")
            for suggestion in apostrophe_suggestions:
                print(f"    - {suggestion}")
        else:
            print(f"  ✅ No apostrophe warnings")
        
        # Show all suggestions for context
        other_suggestions = [s for s in suggestions if "apostrophe" not in s.lower()]
        if other_suggestions:
            print(f"  ℹ️  Other suggestions: {len(other_suggestions)}")

def test_specific_examples():
    """Test specific examples from the user request"""
    
    print("\n" + "=" * 60)
    print("SPECIFIC EXAMPLES TEST")
    print("=" * 60)
    
    examples = [
        ("Tharun's laptop", "Should be recognized as possessive (laptop of Tharun)"),
        ("The API's documentation", "Should be recognized as possessive (documentation of the API)"),
        ("Download all PDF's", "Should suggest this is likely plural misuse"),
        ("The server's CPU's", "Mixed case - one possessive, one potentially plural"),
    ]
    
    for example, expectation in examples:
        print(f"\nExample: {example}")
        print(f"Expected: {expectation}")
        
        suggestions = check(example)
        apostrophe_suggestions = [s for s in suggestions if "apostrophe" in s.lower()]
        
        if apostrophe_suggestions:
            print(f"Result: Warning generated")
            for suggestion in apostrophe_suggestions:
                print(f"  - {suggestion}")
        else:
            print(f"Result: No warnings (recognized as correct usage)")

if __name__ == "__main__":
    test_apostrophe_rule()
    test_specific_examples()
