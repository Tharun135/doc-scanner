#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.rules.grammar_rules import check

# Test the exact content from the user's message
test_content = '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.'

print("Testing exact user content:")
print(f"Content: {test_content}")
print()

results = check(test_content)
print(f"Found {len(results)} suggestions:")
for suggestion in results:
    print(f"- {suggestion}")

if len(results) == 0:
    print("✅ SUCCESS: No false positive detected!")
else:
    print("❌ ISSUE: Still being flagged")
