#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.rules.grammar_rules import check

# Test that other grammar rules still work
test_content = '''# Title

this sentence starts with lowercase and should be flagged.

Some normal text that should be fine.'''

print("Testing that other grammar rules still work:")
print(f"Content:\n{test_content}")
print()

results = check(test_content)
print(f"Grammar rule suggestions: {len(results)}")
for suggestion in results:
    print(f"  - {suggestion}")

if len(results) > 0:
    print("✅ Other grammar rules are still functioning!")
else:
    print("ℹ️ No other grammar issues detected in test content")
