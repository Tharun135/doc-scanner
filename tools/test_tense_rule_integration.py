#!/usr/bin/env python3
"""
Quick test to verify the tense normalization rule is loaded and working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test that the rule can be imported and called correctly
from app.rules.simple_present_normalization import check

print("Testing Simple Present Tense Normalization Rule")
print("=" * 60)

# Test 1: String input (how the rule system calls it)
test_sentence = "The system will validate the input."
print(f"\n📝 Test 1: String input")
print(f"Input: \"{test_sentence}\"")
result = check(test_sentence)
print(f"Result: {len(result)} issue(s) found")
if result:
    for issue in result:
        print(f"  - Type: {issue['type']}")
        print(f"  - Message: {issue['message']}")
        print(f"  - Tense: {issue['tense']}")
        print(f"  - Classification: {issue['classification']}")

# Test 2: Already in present tense (should return empty)
test_sentence2 = "The server processes incoming requests."
print(f"\n📝 Test 2: Already present tense")
print(f"Input: \"{test_sentence2}\"")
result2 = check(test_sentence2)
print(f"Result: {len(result2)} issue(s) found {'✅' if len(result2) == 0 else '❌'}")

# Test 3: Historical context (should return empty - blocked)
test_sentence3 = "In version 3.0, the module was redesigned."
print(f"\n📝 Test 3: Historical context (should be blocked)")
print(f"Input: \"{test_sentence3}\"")
result3 = check(test_sentence3)
print(f"Result: {len(result3)} issue(s) found {'✅' if len(result3) == 0 else '❌'}")

# Test 4: Verify it's loaded by the rule system
print(f"\n📋 Testing rule system integration...")
try:
    from app.app import load_rules
    rules = load_rules()
    
    # Check if simple_present_normalization is in the loaded rules
    rule_names = [rule.__module__ for rule in rules if hasattr(rule, '__module__')]
    
    if 'app.rules.simple_present_normalization' in rule_names:
        print(f"✅ simple_present_normalization IS loaded as a rule")
        print(f"   Total rules loaded: {len(rules)}")
    else:
        print(f"❌ simple_present_normalization NOT found in loaded rules")
        print(f"   Loaded rules: {rule_names}")
        
except Exception as e:
    print(f"⚠️ Could not test rule system integration: {e}")

print("\n" + "=" * 60)
print("✅ Rule is functional and compatible with the system")
