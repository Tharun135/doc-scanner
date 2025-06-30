#!/usr/bin/env python3
"""
Test script to verify that can_may_terms rule deduplication works correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.can_may_terms import check

def test_can_may_deduplication():
    """Test that can/may suggestions are not duplicated"""
    
    # Test sentence with "can" that should get only one suggestion
    test_sentence = "You can configure an IEC 61850 data source in the Common Configurator."
    print(f"Testing sentence: {test_sentence}")
    
    suggestions = check(test_sentence)
    print(f"Number of suggestions returned: {len(suggestions)}")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"Suggestion {i}: {suggestion}")
    
    # Test sentence with "can" and "permission" - should prioritize permission suggestion
    permission_sentence = "You can access files if you have permission to do so."
    print(f"\nTesting permission sentence: {permission_sentence}")
    
    permission_suggestions = check(permission_sentence)
    print(f"Number of suggestions returned: {len(permission_suggestions)}")
    
    for i, suggestion in enumerate(permission_suggestions, 1):
        print(f"Suggestion {i}: {suggestion}")
    
    # Test sentence with multiple "can" instances - should get one suggestion per sentence
    multi_can_sentence = "You can configure the system. You can also modify the settings."
    print(f"\nTesting multi-can sentence: {multi_can_sentence}")
    
    multi_suggestions = check(multi_can_sentence)
    print(f"Number of suggestions returned: {len(multi_suggestions)}")
    
    for i, suggestion in enumerate(multi_suggestions, 1):
        print(f"Suggestion {i}: {suggestion}")
    
    # Test with "may" 
    may_sentence = "This may cause issues. This may also affect performance."
    print(f"\nTesting may sentence: {may_sentence}")
    
    may_suggestions = check(may_sentence)
    print(f"Number of suggestions returned: {len(may_suggestions)}")
    
    for i, suggestion in enumerate(may_suggestions, 1):
        print(f"Suggestion {i}: {suggestion}")
    
    return len(suggestions), len(permission_suggestions), len(multi_suggestions), len(may_suggestions)

if __name__ == "__main__":
    print("Testing can_may_terms deduplication...")
    single_count, permission_count, multi_count, may_count = test_can_may_deduplication()
    
    print(f"\nResults:")
    print(f"Single 'can': {single_count} suggestion(s) (expected: 1)")
    print(f"Permission 'can': {permission_count} suggestion(s) (expected: 1)")
    print(f"Multi 'can': {multi_count} suggestion(s) (expected: 2 - one per sentence)")
    print(f"Multi 'may': {may_count} suggestion(s) (expected: 2 - one per sentence)")
    
    if single_count == 1 and permission_count == 1 and multi_count == 2 and may_count == 2:
        print("✅ Test PASSED: Deduplication working correctly")
    else:
        print("❌ Test FAILED: Deduplication not working properly")
