"""Quick test for style_rules upgrade"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import analyze_sentence, load_rules

rules = load_rules()

print("="*80)
print("STYLE RULES (ADVERBS) - UPGRADE VERIFICATION")
print("="*80)

tests = [
    {
        'name': 'Test 6.1: Subjective adverb "properly" (should be no_change)',
        'sentence': 'Here is an example of a properly configured certificate:',
        'expected': 'no_change',
        'rule': 'style_adverbs'
    }
]

for test in tests:
    print(f"\n{test['name']}")
    print(f"Input: {test['sentence']}")
    
    feedback, _, _ = analyze_sentence(test['sentence'], rules)
    
    style_issues = [f for f in feedback if f.get('rule') == test['rule']]
    
    if style_issues:
        issue = style_issues[0]
        decision = issue.get('decision_type', 'NOT SET')
        rationale = issue.get('reviewer_rationale', 'NOT SET')
        
        print(f"  Decision: {decision}")
        print(f"  Rationale: {rationale[:80]}...")
        
        if decision == test['expected']:
            print(f"  ✓ PASS - Correct decision type")
        else:
            print(f"  ✗ FAIL - Expected '{test['expected']}', got '{decision}'")
    else:
        print(f"  ✗ FAIL - No style issue detected")

print(f"\n{'='*80}\n")
