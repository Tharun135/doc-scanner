#!/usr/bin/env python3
"""
Test the capitalization fix functionality specifically
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import get_rule_specific_correction

def test_capitalization_fix():
    """Test the capitalization fix directly"""
    
    # Test case 1: Basic capitalization
    sentence = "it is in ISO 8601 Zulu format."
    feedback = "Start sentences with a capital letter."
    rule_id = "style"
    
    print(f"🔍 Testing capitalization fix:")
    print(f"  Input: '{sentence}'")
    print(f"  Feedback: '{feedback}'")
    print(f"  Rule ID: '{rule_id}'")
    
    result = get_rule_specific_correction(sentence, rule_id, feedback)
    
    print(f"  Output: '{result}'")
    print(f"  ✅ Success: {result != sentence and result[0].isupper()}")
    
    # Test case 2: Already capitalized
    sentence2 = "It is in ISO 8601 Zulu format."
    result2 = get_rule_specific_correction(sentence2, rule_id, feedback)
    
    print(f"\n🔍 Testing already capitalized:")
    print(f"  Input: '{sentence2}'")
    print(f"  Output: '{result2}'")
    print(f"  ✅ Unchanged: {result2 == sentence2}")
    
    # Test case 3: Different feedback should not trigger capitalization
    sentence3 = "it is in ISO 8601 Zulu format."
    feedback3 = "This is passive voice."
    result3 = get_rule_specific_correction(sentence3, rule_id, feedback3)
    
    print(f"\n🔍 Testing different feedback:")
    print(f"  Input: '{sentence3}'")
    print(f"  Feedback: '{feedback3}'")
    print(f"  Output: '{result3}'")
    print(f"  ✅ Not capitalized: {result3 == sentence3}")

if __name__ == "__main__":
    test_capitalization_fix()
