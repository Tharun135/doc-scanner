#!/usr/bin/env python3

import sys
sys.path.append('.')

# Import all the rules individually to test them
from app.rules import grammar_rules, style_rules, passive_voice, terminology_rules, consistency_rules, long_sentence, vague_terms, verb_tense

# Test content
test_content = '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.'

print("Testing all rules individually:")
print(f"Content: {test_content}")
print()

# Test each rule
rules = [
    ("Grammar Rules", grammar_rules.check),
    ("Style Rules", style_rules.check),
    ("Passive Voice", passive_voice.check),
    ("Terminology Rules", terminology_rules.check),
    ("Consistency Rules", consistency_rules.check),
    ("Long Sentence", long_sentence.check),
    ("Vague Terms", vague_terms.check),
    ("Verb Tense", lambda content: verb_tense.check_verb_tense(content, content)),
]

total_suggestions = 0

for rule_name, rule_function in rules:
    try:
        suggestions = rule_function(test_content)
        print(f"{rule_name}: {len(suggestions)} suggestions")
        if suggestions:
            for suggestion in suggestions:
                if isinstance(suggestion, dict):
                    print(f"  - {suggestion.get('message', suggestion)}")
                else:
                    print(f"  - {suggestion}")
            total_suggestions += len(suggestions)
    except Exception as e:
        print(f"{rule_name}: ERROR - {e}")

print(f"\nTotal suggestions across all rules: {total_suggestions}")

if total_suggestions == 0:
    print("✅ No rules are flagging this content!")
else:
    print("❌ Some rules are still flagging this content")
