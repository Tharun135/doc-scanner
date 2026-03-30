"""Quick test for simple_present_normalization rule upgrade"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import analyze_sentence, load_rules

rules = load_rules()

print("="*80)
print("SIMPLE PRESENT TENSE RULE - UPGRADE VERIFICATION")
print("="*80)

tests = [
    {
        'name': 'Test 3.1: Future tense (should be rewrite)',
        'sentence': 'The system will validate the configuration.',
        'expected': 'rewrite',
        'rule': 'simple_present_tense'
    },
    {
        'name': 'Test 3.2: Historical context (should be no_change)',
        'sentence': 'In version 3.0, the system was redesigned.',
        'expected': 'no_change',
        'rule': 'simple_present_tense'
    }
]

for test in tests:
    print(f"\n{test['name']}")
    print(f"Input: {test['sentence']}")
    
    feedback, _, _ = analyze_sentence(test['sentence'], rules)
    
    tense_issues = [f for f in feedback if f.get('rule') == test['rule']]
    
    if tense_issues:
        issue = tense_issues[0]
        decision = issue.get('decision_type', 'NOT SET')
        rationale = issue.get('reviewer_rationale', 'NOT SET')
        
        print(f"  Decision: {decision}")
        print(f"  Rationale: {rationale[:80]}...")
        
        if decision == test['expected']:
            print(f"  ✓ PASS - Correct decision type")
        else:
            print(f"  ✗ FAIL - Expected '{test['expected']}', got '{decision}'")
    else:
        print(f"  ✗ FAIL - No tense issue detected")

print(f"\n{'='*80}\n")
