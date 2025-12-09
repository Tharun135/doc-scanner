#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import re
from app.rules.cross_references import check

# Test the problematic sentence
test_sentence = "If the files chosen for upload consume more than 90% of the available space, an error message appears, warning that there may not be enough storage space to accommodate the selected files."

print("Testing URL detection false positive:\n")
print(f"Sentence: {test_sentence}")
print()

# Test the regex pattern directly first
url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'
urls_found = re.findall(url_pattern, test_sentence, flags=re.IGNORECASE)

print(f"URLs found by regex: {urls_found}")
print()

# Now test the actual rule
try:
    from app.rules.cross_references import check
    suggestions = check(test_sentence)
    print(f"Rule suggestions: {suggestions}")
except Exception as e:
    print(f"Error testing rule: {e}")
    print("Testing just the regex pattern instead...")
print()

print("=" * 60)
print("ANALYSIS:")
print("The regex pattern is matching text that contains dots followed by 2+ letters.")
print("In this case, it's probably matching parts like 'space to' or similar.")
print("The rule needs to be more specific to avoid false positives.")
