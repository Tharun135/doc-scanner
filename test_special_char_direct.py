#!/usr/bin/env python3

import sys
sys.path.append('app')

# Test the special character rule directly
from app.rules.special_characters import check

test_text = "Use this & that feature."
print(f"Testing text: '{test_text}'")

result = check(test_text)
print(f"Rule result: {result}")

# Test with multiple ampersands
test_text2 = "Use this & that & another feature."
print(f"\nTesting text: '{test_text2}'")

result2 = check(test_text2)
print(f"Rule result: {result2}")
