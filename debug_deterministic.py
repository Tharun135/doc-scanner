#!/usr/bin/env python3
"""
Debug the deterministic rewrite function specifically
"""
import sys
sys.path.append('app')

from app.services.enrichment import _create_deterministic_rewrite

def debug_deterministic_rewrite():
    print("🔍 DEBUGGING: _create_deterministic_rewrite function")
    print("=" * 60)
    
    test_cases = [
        {
            "feedback": "Avoid passive voice in sentence: 'Tags are only defined for sensors.'",
            "sentence": "Tags are only defined for sensors.",
            "expected": "Should convert passive to active voice"
        },
        {
            "feedback": "Avoid passive voice in sentence: 'A data source has already been created.'",
            "sentence": "A data source has already been created.",
            "expected": "Should handle 'has been created' pattern"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['expected']}")
        print(f"Original: '{test['sentence']}'")
        print(f"Feedback: '{test['feedback']}'")
        
        result = _create_deterministic_rewrite(test['feedback'], test['sentence'])
        
        print(f"Result: '{result}'")
        
        if result == test['sentence']:
            print("❌ FAILED: Returned original sentence unchanged")
        elif result.startswith(("Improve clarity:", "Revise for clarity:")):
            print("⚠️  WARNING: Using generic fallback")
        elif result != test['sentence']:
            print("✅ SUCCESS: Generated different sentence")
        else:
            print("❓ UNKNOWN: Needs investigation")

if __name__ == "__main__":
    debug_deterministic_rewrite()
