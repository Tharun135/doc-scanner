#!/usr/bin/env python3
"""
Test script to verify the updated capital letter rule excludes technical codes
"""

import sys
import os

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

# Import the grammar rules check function directly
from app.rules.grammar_rules import check

def test_capital_letter_rule():
    """Test the capital letter rule with various inputs"""
    
    test_cases = [
        # Technical codes that should NOT trigger the rule
        ("ie/d/j/simatic/v1/slmp1/dp/r//default", False),
        ("api/v1/users/profile", False),
        ("src/components/header.js", False),
        ("config.json", False),
        ("object.method()", False),
        ("variable.property", False),
        ("https://example.com/path", False),
        ("http://api.service.com", False),
        
        # Regular sentences that SHOULD trigger the rule
        ("this is a sentence that should start with capital", True),
        ("another lowercase sentence", True),
        
        # Sentences that should NOT trigger (already proper)
        ("This is a proper sentence.", False),
        ("Another proper sentence with capital.", False),
        
        # Markdown info blocks that should NOT trigger
        ('info "This is a notice"', False),
        ('warning "This is a warning"', False),
    ]
    
    print("Testing capital letter rule with technical code exclusions...")
    print("=" * 60)
    
    all_passed = True
    
    for i, (test_text, should_trigger) in enumerate(test_cases, 1):
        suggestions = check(test_text)
        capital_suggestions = [s for s in suggestions if "Start sentences with a capital letter" in s]
        
        triggered = len(capital_suggestions) > 0
        passed = triggered == should_trigger
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{i:2d}. {status} | '{test_text}'")
        
        if not passed:
            all_passed = False
            print(f"    Expected: {'Should trigger' if should_trigger else 'Should NOT trigger'}")
            print(f"    Actual: {'Triggered' if triggered else 'Did not trigger'}")
            if capital_suggestions:
                print(f"    Suggestion: {capital_suggestions[0]}")
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests PASSED! The rule correctly excludes technical codes.")
    else:
        print("❌ Some tests FAILED. Check the rule implementation.")
    
    return all_passed

if __name__ == "__main__":
    test_capital_letter_rule()
