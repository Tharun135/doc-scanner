#!/usr/bin/env python3

"""
Test script to see what punctuation issues are being detected.
"""

import sys
sys.path.append('app')

from app.rules.punctuation import check

# Test sentences with different punctuation
test_sentences = [
    "This is a normal sentence.",
    "This sentence has a period at the end.",
    "This has a hyphen-word combination.",
    "This uses -- double hyphens.",
    "This sentence ends with a period.",
    "Multiple sentences. With periods. At the end.",
    "No punctuation issues here",
    "This is a compound-word sentence."
]

print("Testing punctuation detection:")
print("=" * 50)

for i, sentence in enumerate(test_sentences, 1):
    print(f"\n{i}. Testing: '{sentence}'")
    issues = check(sentence)
    if issues:
        print(f"   Issues found: {len(issues)}")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("   No issues found")

print("\n" + "=" * 50)
print("Test completed!")
