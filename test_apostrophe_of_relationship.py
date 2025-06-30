#!/usr/bin/env python3
"""
Test script to verify that the apostrophe rule correctly handles the "of" relationship clarification.
This test checks that the rule allows apostrophes for possession (the "of" relationship) 
but warns against their use for plurals.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.rules import special_characters

def test_apostrophe_of_relationship():
    """Test that apostrophe rule correctly explains the 'of' relationship for possession."""
    
    print("Testing apostrophe rule with 'of' relationship clarification...")
    
    # Test cases for valid possession (should NOT be flagged)
    valid_possessive_cases = [
        "Tharun's laptop is on the desk.",  # Tharun's laptop = laptop of Tharun
        "The user's guide is helpful.",     # user's guide = guide of the user
        "Sarah's documentation is clear.",  # Sarah's documentation = documentation of Sarah
        "The company's policy changed.",    # company's policy = policy of the company
        "Microsoft's software is popular."  # Microsoft's software = software of Microsoft
    ]
    
    # Test cases for plural misuse (should be flagged)
    plural_misuse_cases = [
        "API's are important for integration.",     # Should be "APIs are"
        "The application's have many features.",    # Should be "applications have"
        "Database's were updated yesterday.",       # Should be "databases were"
    ]
    
    print("\n=== Testing Valid Possessive Cases (should NOT be flagged) ===")
    for i, text in enumerate(valid_possessive_cases, 1):
        print(f"\nTest {i}: '{text}'")
        suggestions = special_characters.check(text)
        apostrophe_suggestions = [s for s in suggestions if "apostrophe" in s.lower()]
        
        if apostrophe_suggestions:
            print(f"  ❌ FAILED: Got unexpected apostrophe suggestion: {apostrophe_suggestions[0]}")
        else:
            print(f"  ✅ PASSED: No apostrophe warnings (correct for possession)")
    
    print("\n=== Testing Plural Misuse Cases (should be flagged) ===")
    for i, text in enumerate(plural_misuse_cases, 1):
        print(f"\nTest {i}: '{text}'")
        suggestions = special_characters.check(text)
        apostrophe_suggestions = [s for s in suggestions if "apostrophe" in s.lower()]
        
        if apostrophe_suggestions:
            print(f"  ✅ PASSED: Got expected apostrophe warning: {apostrophe_suggestions[0]}")
            # Check if the suggestion mentions the "of" relationship
            if "of" in apostrophe_suggestions[0]:
                print(f"  ✅ BONUS: Suggestion includes 'of' relationship explanation")
            else:
                print(f"  ⚠️  NOTE: Suggestion doesn't mention 'of' relationship")
        else:
            print(f"  ❌ FAILED: Expected apostrophe warning but got none")
    
    print("\n=== Testing Explanation Quality ===")
    # Test a specific case to see the exact message
    test_text = "The API's are well documented."
    suggestions = special_characters.check(test_text)
    apostrophe_suggestions = [s for s in suggestions if "apostrophe" in s.lower()]
    
    if apostrophe_suggestions:
        suggestion = apostrophe_suggestions[0]
        print(f"Sample suggestion: '{suggestion}'")
        
        # Check for key elements in the suggestion
        has_of_relationship = "of" in suggestion.lower()
        has_possession_example = "tharun's laptop" in suggestion.lower()
        has_clear_guidance = "possession" in suggestion.lower()
        
        print(f"  Contains 'of' relationship: {has_of_relationship}")
        print(f"  Contains possession example: {has_possession_example}")
        print(f"  Contains 'possession' guidance: {has_clear_guidance}")
        
        if has_of_relationship and has_possession_example and has_clear_guidance:
            print("  ✅ Suggestion quality: EXCELLENT - includes all key clarifications")
        elif has_of_relationship or has_possession_example:
            print("  ✅ Suggestion quality: GOOD - includes some clarification")
        else:
            print("  ⚠️  Suggestion quality: BASIC - could be more explanatory")
    else:
        print("No apostrophe suggestion found for test case")

if __name__ == "__main__":
    test_apostrophe_of_relationship()
