#!/usr/bin/env python3
"""
Test script to verify that modal verb rule deduplication works correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.simple_present_tense import check

def test_modal_deduplication():
    """Test that modal verb suggestions are not duplicated"""
    
    test_sentence = "You can configure an IEC 61850 data source in the Common Configurator."
    print(f"Testing sentence: {test_sentence}")
    
    suggestions = check(test_sentence)
    print(f"Number of suggestions returned: {len(suggestions)}")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"Suggestion {i}: {suggestion}")
    
    # Test with multiple modal verbs in the same sentence
    multi_modal_sentence = "You can configure the system and you can also modify the settings."
    print(f"\nTesting multi-modal sentence: {multi_modal_sentence}")
    
    multi_suggestions = check(multi_modal_sentence)
    print(f"Number of suggestions returned: {len(multi_suggestions)}")
    
    for i, suggestion in enumerate(multi_suggestions, 1):
        print(f"Suggestion {i}: {suggestion}")
    
    return len(suggestions), len(multi_suggestions)

if __name__ == "__main__":
    print("Testing modal verb deduplication...")
    single_count, multi_count = test_modal_deduplication()
    
    print(f"\nExpected: 1 suggestion for single modal, 1 suggestion for multi-modal")
    print(f"Actual: {single_count} suggestion(s) for single modal, {multi_count} suggestion(s) for multi-modal")
    
    if single_count == 1 and multi_count == 1:
        print("✅ Test PASSED: Deduplication working correctly")
    else:
        print("❌ Test FAILED: Deduplication not working")
