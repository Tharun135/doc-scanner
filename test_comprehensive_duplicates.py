#!/usr/bin/env python3
"""
Comprehensive test to verify duplicate suggestions are fixed
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.simple_present_tense import check as check_tense
from app.rules.can_may_terms import check as check_can_may

def test_original_duplicate_issue():
    """Test the original issue that was causing duplicates"""
    
    # Original problematic sentence
    test_sentence = "You can configure an IEC 61850 data source in the Common Configurator."
    print(f"Testing original issue with sentence: {test_sentence}")
    
    # Test simple_present_tense rule
    print("\n=== Testing simple_present_tense.py rule ===")
    tense_suggestions = check_tense(test_sentence)
    print(f"Number of suggestions: {len(tense_suggestions)}")
    for i, suggestion in enumerate(tense_suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Test can_may_terms rule
    print("\n=== Testing can_may_terms.py rule ===")
    can_may_suggestions = check_can_may(test_sentence)
    print(f"Number of suggestions: {len(can_may_suggestions)}")
    for i, suggestion in enumerate(can_may_suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Check if we would get duplicates when both rules run (simulate what happens in the app)
    print("\n=== Combined suggestions (simulating app behavior) ===")
    all_suggestions = tense_suggestions + can_may_suggestions
    print(f"Total suggestions from both rules: {len(all_suggestions)}")
    
    # Look for potential duplicates
    duplicate_check = {}
    for suggestion in all_suggestions:
        # Extract the main part of the suggestion (ignore specific rewrites)
        main_suggestion = suggestion.split("Original:")[0].strip()
        if main_suggestion in duplicate_check:
            duplicate_check[main_suggestion] += 1
        else:
            duplicate_check[main_suggestion] = 1
    
    print("\nDuplicate analysis:")
    duplicates_found = False
    for suggestion, count in duplicate_check.items():
        if count > 1:
            print(f"  DUPLICATE ({count}x): {suggestion}")
            duplicates_found = True
        else:
            print(f"  UNIQUE (1x): {suggestion}")
    
    return duplicates_found, len(all_suggestions)

def test_edge_cases():
    """Test various edge cases"""
    
    test_cases = [
        "You can configure this and you can also modify that.",  # Multiple cans in one sentence
        "You can access files if you have permission.",  # Can + permission
        "This may work and this may also fail.",  # Multiple mays
        "You could try this approach.",  # Could usage
        "You can, may, or might consider this option."  # Multiple modals
    ]
    
    print("\n" + "="*60)
    print("EDGE CASE TESTING")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {test_case}")
        
        tense_sug = check_tense(test_case)
        can_may_sug = check_can_may(test_case)
        
        print(f"  simple_present_tense: {len(tense_sug)} suggestion(s)")
        print(f"  can_may_terms: {len(can_may_sug)} suggestion(s)")
        
        # Check for reasonable suggestion counts
        total_suggestions = len(tense_sug) + len(can_may_sug)
        if total_suggestions > 3:  # Arbitrary threshold for "too many"
            print(f"  ⚠️  Warning: {total_suggestions} total suggestions might be excessive")
        else:
            print(f"  ✅ Reasonable: {total_suggestions} total suggestions")

if __name__ == "__main__":
    print("COMPREHENSIVE DUPLICATE SUGGESTION TEST")
    print("="*50)
    
    # Test original issue
    duplicates_found, suggestion_count = test_original_duplicate_issue()
    
    # Test edge cases
    test_edge_cases()
    
    # Final assessment
    print("\n" + "="*50)
    print("FINAL ASSESSMENT")
    print("="*50)
    
    if not duplicates_found:
        print("✅ SUCCESS: No duplicate suggestions found in original problematic sentence")
    else:
        print("❌ FAILURE: Duplicate suggestions still found")
    
    print(f"Original sentence generated {suggestion_count} total suggestions")
    print("Expected: 1-2 suggestions (one per rule, different purposes)")
    
    if suggestion_count <= 2 and not duplicates_found:
        print("\n🎉 OVERALL RESULT: Duplicate issue appears to be FIXED!")
    else:
        print("\n⚠️  OVERALL RESULT: Issues may still exist")
