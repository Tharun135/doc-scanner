#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

from app.rules.concise_simple_words import check

# Test case for the "effectively with" issue
test_text = """
The system can manage data effectively with advanced algorithms.
Users can work effectively with the new interface.
The process works effectively with minimal configuration.
"""

print("Testing unnecessary modifier detection:\n")

suggestions = check(test_text)

for suggestion in suggestions:
    print(f"Suggestion: {suggestion}")
    if "effectively with" in suggestion:
        print(f"  ⚠️  This is the problematic suggestion!")
    print()

print("=" * 60)
print("ISSUE ANALYSIS:")
print("The rule is finding 'effectively with' and suggesting 'with'")
print("But 'effectively with' is often appropriate in technical writing")
print("The highlighting may fail because the sentence structure differs from the match")
