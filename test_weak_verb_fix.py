#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

from app.rules.concise_simple_words import check

# Test cases
test_cases = [
    "There are no scroll bars needed, as there is no requirement to navigate screens vertically or horizontally.",
    "There are three options available for configuration.",
    "There is a setting that controls this behavior.",
    "There are not any issues with the current implementation.",
    "There are several methods to accomplish this task."
]

print("Testing weak verb construction rule fixes:\n")

for i, test_case in enumerate(test_cases, 1):
    print(f"Test {i}: {test_case}")
    suggestions = check(test_case)
    weak_verb_suggestions = [s for s in suggestions if "Weak verb construction" in s]
    
    if weak_verb_suggestions:
        for suggestion in weak_verb_suggestions:
            print(f"  → {suggestion}")
    else:
        print("  → No weak verb construction suggestions (GOOD for negative constructions)")
    print()
