#!/usr/bin/env python3

"""
Test the updated hyphen/dash detection to ensure it works correctly.
"""

import sys
sys.path.append('app')

from app.rules.punctuation import _check_hyphen_dash

# Test sentences with various scenarios
test_cases = [
    # Should NOT trigger hyphen/dash issues (normal sentences with periods)
    ("This is a normal sentence.", "Should be no issues"),
    ("This sentence ends with a period.", "Should be no issues"),
    ("Well written document here.", "Should be no issues"),
    
    # SHOULD trigger hyphen/dash issues
    ("This uses -- double hyphens for emphasis", "Should detect double hyphen issue"),
    ("Some text - with spaced hyphen - here", "Should detect spaced hyphen issue"),
    ("This is a badly written sentence", "Should detect compound modifier issue"),
    
    # Edge cases
    ("Sentence with -- double hyphen.", "Should detect double hyphen even with period"),
    ("Text with - spaced hyphen - in middle.", "Should detect spaced hyphen even with period"),
]

print("Testing updated hyphen/dash detection:")
print("=" * 70)

for sentence, expected in test_cases:
    issues = _check_hyphen_dash(sentence)
    print(f"\nSentence: '{sentence}'")
    print(f"Expected: {expected}")
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    print("-" * 40)

print("\nTest completed!")
