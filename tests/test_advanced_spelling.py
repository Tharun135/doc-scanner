#!/usr/bin/env python3
"""
Test script for advanced spelling checker features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.spelling_checker import check, SPELL_CHECKERS_AVAILABLE

def test_advanced_spelling():
    print("=== Testing Advanced Spelling Checker ===")
    print(f"PySpellChecker available: {SPELL_CHECKERS_AVAILABLE['pyspellchecker']}")
    print()
    
    # Test with various types of content
    test_cases = [
        # Basic misspellings
        "This sentance has mispelled words.",
        
        # Technical content (should avoid false positives)
        "Configure the API endpoint using JSON and OAuth authentication.",
        
        # Mixed content
        "The confguration file needs to be upated for the new dependancy.",
        
        # Content with proper nouns and technical terms
        "Microsoft Azure provides scalabilty for enterprize applications.",
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_text}")
        suggestions = check(test_text)
        if suggestions:
            print(f"  Found {len(suggestions)} spelling issues:")
            for j, suggestion in enumerate(suggestions, 1):
                print(f"    {j}. {suggestion}")
        else:
            print("  No spelling issues found.")
        print()
    
    print("=== Advanced Test Completed ===")

if __name__ == "__main__":
    test_advanced_spelling()
