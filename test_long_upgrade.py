"""Quick test for long_sentence rule upgrade"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import analyze_sentence, load_rules

rules = load_rules()

print("="*80)
print("LONG SENTENCE RULE - UPGRADE VERIFICATION")
print("="*80)

tests = [
    {
        'name': 'Test 4.1: Simple long sentence (should be rewrite)',
        'sentence': 'The system reads the configuration file and validates all the parameters and checks the syntax and verifies the settings before starting the application and loading all the required modules and dependencies.',
        'expected': 'rewrite',
        'rule': 'long_sentence'
    },
    {
        'name': 'Test 4.2: Conditional/compliance sentence (should be explain)',
        'sentence': 'The server certificate must include the IP address in the SAN field or the fully qualified domain name if it is registered in DNS or a wildcard certificate if multiple subdomains are required.',
        'expected': 'explain',
        'rule': 'long_sentence'
    }
]

for test in tests:
    print(f"\n{test['name']}")
    print(f"Input: {test['sentence']}")
    
    feedback, _, _ = analyze_sentence(test['sentence'], rules)
    
    long_issues = [f for f in feedback if f.get('rule') == test['rule']]
    
    if long_issues:
        issue = long_issues[0]
        decision = issue.get('decision_type', 'NOT SET')
        rationale = issue.get('reviewer_rationale', 'NOT SET')
        
        print(f"  Decision: {decision}")
        print(f"  Rationale: {rationale[:80]}...")
        
        if decision == test['expected']:
            print(f"  ✓ PASS - Correct decision type")
        else:
            print(f"  ✗ FAIL - Expected '{test['expected']}', got '{decision}'")
    else:
        print(f"  ⚠ No long sentence issue detected (sentence may be under 25 words)")

print(f"\n{'='*80}\n")
