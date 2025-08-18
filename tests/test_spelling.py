#!/usr/bin/env python3
"""
Test script for the spelling checker rule.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.spelling_checker import check, check_common_misspellings, extract_words_for_spelling

def test_spelling_checker():
    print("=== Testing Spelling Checker ===")
    
    # Test text with known misspellings
    test_text = "This sentance has mispelled words like recieve and seperate. The performace is good."
    print(f"Test text: {test_text}")
    print()
    
    # Test word extraction
    print("1. Testing word extraction:")
    words = extract_words_for_spelling(test_text)
    print(f"Extracted words: {words}")
    print()
    
    # Test common misspellings
    print("2. Testing common misspellings detection:")
    common_suggestions = check_common_misspellings(test_text)
    print(f"Found {len(common_suggestions)} common misspelling suggestions:")
    for i, suggestion in enumerate(common_suggestions, 1):
        print(f"   {i}. {suggestion}")
    print()
    
    # Test full spelling check
    print("3. Testing full spelling check:")
    all_suggestions = check(test_text)
    print(f"Found {len(all_suggestions)} total spelling suggestions:")
    for i, suggestion in enumerate(all_suggestions, 1):
        print(f"   {i}. {suggestion}")
    print()
    
    print("=== Test completed ===")

if __name__ == "__main__":
    test_spelling_checker()
