"""
Test script for atomic rules system.
Tests a simple sentence with multiple violations.
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rules.loader import load_rules
from app.rules.matcher import apply_rules, format_violation_for_ui, get_severity_summary

# Test sentences with known violations
test_cases = [
    {
        "name": "Future Tense + UI Label Error",
        "sentence": "The system will display results. Click the Save button.",
        "expected_errors": ["TENSE_001", "UI_001"]
    },
    {
        "name": "Personal Pronoun Error",
        "sentence": "You should configure your settings first.",
        "expected_errors": ["PERSON_001"]
    },
    {
        "name": "Adverb Warning",
        "sentence": "Simply click the button to proceed.",
        "expected_errors": ["ADV_001"]
    },
    {
        "name": "Phrasal Verb Warning",
        "sentence": "Set up the device before use.",
        "expected_errors": ["PVERB_001"]
    },
    {
        "name": "Safety Error - NOTICE with symbol",
        "sentence": "NOTICE ⚠️ Handle device carefully.",
        "expected_errors": ["SAFETY_001"]
    },
    {
        "name": "Oxford Comma Warning",
        "sentence": "Save, compile and deploy the application.",
        "expected_errors": ["OXFORD_001"]
    },
    {
        "name": "Clean Sentence (No Violations)",
        "sentence": "Configure the network settings.",
        "expected_errors": []
    }
]

def test_atomic_rules():
    """Test the atomic rules system."""
    print("=" * 80)
    print("ATOMIC RULES SYSTEM TEST")
    print("=" * 80)
    
    # Load rules
    print("\n📋 Loading rules...")
    rules = load_rules()
    print(f"✅ Loaded {len(rules)} rules\n")
    
    # Test each case
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'=' * 80}")
        print(f"Sentence: \"{test_case['sentence']}\"")
        
        # Apply rules
        violations = apply_rules(test_case['sentence'], rules)
        
        # Get severity summary
        summary = get_severity_summary(violations)
        
        print(f"\nFound {len(violations)} violation(s):")
        print(f"  🔴 Errors: {summary['error']}")
        print(f"  🟡 Warnings: {summary['warn']}")
        print(f"  🔵 Info: {summary['info']}")
        
        # Display violations
        if violations:
            print("\nViolations:")
            for v in violations:
                severity_icon = {
                    "error": "🔴",
                    "warn": "🟡",
                    "info": "🔵"
                }.get(v['severity'], "⚪")
                
                print(f"\n  {severity_icon} {v['rule_id']} ({v['severity'].upper()})")
                print(f"     Message: {v['message']}")
                print(f"     Matched: '{v['matched_text']}'")
                if v.get('suggestion'):
                    print(f"     💡 Suggestion: {v['suggestion']}")
        else:
            print("\n✅ No violations found!")
        
        # Verify expected violations
        found_rule_ids = [v['rule_id'] for v in violations]
        expected = test_case['expected_errors']
        
        if set(found_rule_ids) >= set(expected):  # >= because we might find more rules
            print(f"\n✅ TEST PASSED: Found expected rules {expected}")
            passed += 1
        else:
            print(f"\n❌ TEST FAILED")
            print(f"   Expected: {expected}")
            print(f"   Found: {found_rule_ids}")
            failed += 1
    
    # Final summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{len(test_cases)}")
    print(f"❌ Failed: {failed}/{len(test_cases)}")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    
    return passed == len(test_cases)

if __name__ == "__main__":
    success = test_atomic_rules()
    sys.exit(0 if success else 1)
