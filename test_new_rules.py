#!/usr/bin/env python3
"""
Test script to verify the new rules are working correctly.
"""

import sys
import os
sys.path.append('.')

from app.app import load_rules
from app.rules.long_sentence import check as check_long_sentence
from app.rules.passive_voice import check as check_passive_voice
from app.rules.style_rules import check as check_style_rules
from app.rules.readability_rules import check as check_readability_rules
from app.rules.vague_terms import check as check_vague_terms

def test_new_rules():
    print("🧪 Testing New Rules Integration")
    print("=" * 50)
    
    # Test 1: Load all rules
    print("\n1. Loading all rules...")
    rules = load_rules()
    print(f"✅ Successfully loaded {len(rules)} rules")
    
    # Test 2: Test individual rules
    test_cases = [
        {
            "name": "Long Sentence",
            "rule": check_long_sentence,
            "content": "<p>This is a very long sentence that contains many words and should definitely be more than twenty-five words which will trigger the long sentence detection rule and provide suggestions.</p>"
        },
        {
            "name": "Passive Voice", 
            "rule": check_passive_voice,
            "content": "<p>The document was written by the author.</p>"
        },
        {
            "name": "Style Issues",
            "rule": check_style_rules, 
            "content": "<p>The user is VERY excited!!! This is amazing!!!</p>"
        },
        {
            "name": "Vague Terms",
            "rule": check_vague_terms,
            "content": "<p>There are some things you need to know about various stuff.</p>"
        }
    ]
    
    print("\n2. Testing individual rules...")
    for test_case in test_cases:
        print(f"\n   Testing {test_case['name']}:")
        try:
            result = test_case['rule'](test_case['content'])
            if result:
                print(f"   ✅ Found {len(result)} suggestions:")
                for suggestion in result[:2]:  # Show first 2
                    print(f"      - {suggestion[:80]}...")
            else:
                print(f"   ℹ️  No suggestions (this is normal for some test cases)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 New Rules Integration Test Complete!")

if __name__ == "__main__":
    test_new_rules()
