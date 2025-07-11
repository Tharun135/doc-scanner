#!/usr/bin/env python3

import sys
sys.path.append('app')

# Test the modal verb rule directly
from app.rules.can_may_terms import check

test_text = "You may enter the building after 9 AM."
print(f"Testing text: '{test_text}'")

result = check(test_text)
print(f"Rule result: {result}")

# Test possibility case
test_text2 = "The weather may be nice tomorrow."
print(f"\nTesting text: '{test_text2}'")

result2 = check(test_text2)
print(f"Rule result: {result2}")

# Test mixed case
test_text3 = """
This document contains several issues to test our fixes:
1. Modal verb issues:
   - Permission: You may enter the building after 9 AM.
   - Possibility: The weather may be nice tomorrow.
"""
print(f"\nTesting text: '{test_text3}'")

result3 = check(test_text3)
print(f"Rule result: {result3}")
