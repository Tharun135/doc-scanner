#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.rules.grammar_rules import check

# Test with a clearer grammar issue - sentence starting with lowercase (not in an admonition)
test_content = 'normal sentence that starts with lowercase.'

print("Testing lowercase sentence detection:")
print(f"Content: {repr(test_content)}")
print()

results = check(test_content)
print(f"Grammar rule suggestions: {len(results)}")
for suggestion in results:
    print(f"  - {suggestion}")

# Also test that spacy grammar checks still work if they find subject-verb disagreement
test_content2 = "The dogs runs quickly."

print(f"\nTesting with potential subject-verb disagreement:")
print(f"Content: {repr(test_content2)}")
print()

results2 = check(test_content2)
print(f"Grammar rule suggestions: {len(results2)}")
for suggestion in results2:
    print(f"  - {suggestion}")
