#!/usr/bin/env python3
"""
Test to ensure normal sentence capitalization checking still works
"""

import sys
import os

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.rules.grammar_rules import check

def test_normal_sentences():
    """Test that normal sentences still get flagged appropriately"""
    
    test_cases = [
        # Should trigger capital letter rule
        ("this sentence should start with capital", True),
        ("another example of incorrect capitalization", True),
        ("here is one more test case", True),
        
        # Should NOT trigger (already correct)
        ("This sentence starts correctly.", False),
        ("Another properly capitalized sentence.", False),
        ("Here is a third correct example.", False),
        
        # Mixed content - these start with lowercase so should trigger
        ("the API endpoint is api/v1/users but this sentence needs capital", True),
        ("we use config.json for settings and this also needs capital", True),
    ]
    
    print("Testing normal sentence capitalization...")
    print("=" * 60)
    
    all_passed = True
    
    for i, (test_text, should_trigger) in enumerate(test_cases, 1):
        suggestions = check(test_text)
        capital_suggestions = [s for s in suggestions if "Start sentences with a capital letter" in s]
        
        triggered = len(capital_suggestions) > 0
        passed = triggered == should_trigger
        
        status = "✅ PASS" if passed else "❌ FAIL"
        expected = "Should trigger" if should_trigger else "Should NOT trigger"
        actual = "Triggered" if triggered else "Did not trigger"
        
        print(f"{i:2d}. {status} | '{test_text[:50]}{'...' if len(test_text) > 50 else ''}'")
        print(f"    Expected: {expected} | Actual: {actual}")
        
        if not passed:
            all_passed = False
            print(f"    ❌ MISMATCH!")
            if capital_suggestions:
                print(f"    Suggestion: {capital_suggestions[0]}")
        
        print()
    
    return all_passed

if __name__ == "__main__":
    print("Normal Sentence Capitalization Test")
    print("Ensuring we didn't break existing functionality")
    print("=" * 60)
    
    normal_functionality_works = test_normal_sentences()
    
    print("=" * 60)
    if normal_functionality_works:
        print("🎉 SUCCESS: Normal sentence capitalization checking still works!")
    else:
        print("❌ PROBLEM: Normal functionality has been broken by our changes.")
