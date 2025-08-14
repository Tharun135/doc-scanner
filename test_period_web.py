#!/usr/bin/env python3
"""Test period detection with the web app format."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.punctuation_rules import check_period_placement

# Read test file
with open('test_period_formatting.txt', 'r') as f:
    content = f.read()

print('Testing period detection on formatted content:')
print('=' * 50)
print(f'Content:\n{content}')
print()

# Test the rule directly
suggestions = check_period_placement(content)
print(f'Found {len(suggestions)} period suggestions:')
for i, suggestion in enumerate(suggestions, 1):
    print(f'{i}. {suggestion["message"]}')
    print(f'   Position: {suggestion["start"]}-{suggestion["end"]}')
    print(f'   Text: {suggestion["text"]}')
    print()

# Test highlighting accuracy
print("Verifying position accuracy:")
print("-" * 30)
for i, suggestion in enumerate(suggestions, 1):
    start = suggestion["start"]
    end = suggestion["end"]
    actual_text = content[start:end]
    expected_text = suggestion["text"]
    
    if actual_text == expected_text:
        print(f'✅ Suggestion {i}: Position mapping correct')
    else:
        print(f'❌ Suggestion {i}: Position mapping incorrect')
        print(f'   Expected: {repr(expected_text)}')
        print(f'   Actual:   {repr(actual_text)}')
