"""
Diagnostic Test - What Rules Actually Fire?

This reveals what the current system actually does vs. what tests expect.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import analyze_sentence, load_rules

# Load rules
rules = load_rules()

print("="*80)
print("DIAGNOSTIC: What Rules Actually Fire?")
print("="*80)

test_cases = [
    ("Future tense", "The system will validate the configuration."),
    ("Past tense (historical)", "In version 3.0, the system was redesigned."),
    ("Passive with actor", "The file was created by the system."),
    ("Passive without actor", "Access is restricted for security reasons."),
    ("Long sentence", "The system reads the configuration file and validates the parameters before starting."),
    ("Adverb 'properly'", "Here is an example of a properly configured certificate:"),
    ("Title/heading", "Configuring KEPware server with certificates"),
]

for label, sentence in test_cases:
    print(f"\n{'='*80}")
    print(f"TEST: {label}")
    print(f"INPUT: {sentence}")
    print(f"{'='*80}")
    
    feedback, readability, quality = analyze_sentence(sentence, rules)
    
    if feedback:
        print(f"\n✓ Rules fired: {len(feedback)} issue(s)")
        for idx, item in enumerate(feedback, 1):
            print(f"\n  [{idx}] Rule: {item.get('rule', 'unknown')}")
            print(f"      Message: {item.get('message', '')[:100]}")
            print(f"      Decision type: {item.get('decision_type', 'NOT SET')}")
            print(f"      Rationale: {item.get('reviewer_rationale', 'NOT SET')[:80]}")
            print(f"      Has rewrite: {bool(item.get('ai_suggestion'))}")
    else:
        print(f"\n✗ NO RULES FIRED")
        print(f"   This sentence passed silently through all {len(rules)} rules")

print(f"\n{'='*80}")
print("LOADED RULES:")
print(f"{'='*80}")
for idx, rule in enumerate(rules, 1):
    print(f"{idx}. {rule.__name__} from {rule.__module__}")

print(f"\n{'='*80}")
print("DIAGNOSIS COMPLETE")
print(f"{'='*80}\n")
