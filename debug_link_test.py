#!/usr/bin/env python3
"""Debug why link test case doesn't work."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.punctuation_rules import check_period_placement
import re

text = 'Check out this [great website](https://example.com) for more info'
print(f'Original: {repr(text)}')

# Simulate the cleaning process step by step
cleaned = text
print(f'Step 1 - Original: {repr(cleaned)}')

cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)  # **bold** -> bold
print(f'Step 2 - Bold removed: {repr(cleaned)}')

cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)      # *italic* -> italic
print(f'Step 3 - Italic removed: {repr(cleaned)}')

cleaned = re.sub(r'_([^_]+)_', r'\1', cleaned)        # _italic_ -> italic
print(f'Step 4 - Underscore italic removed: {repr(cleaned)}')

cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)  # [text](url) -> text
print(f'Step 5 - Links removed: {repr(cleaned)}')

cleaned = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', cleaned)  # ![alt](src) -> (empty)
print(f'Step 6 - Images removed: {repr(cleaned)}')

cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)  # `code` -> code
print(f'Step 7 - Code removed: {repr(cleaned)}')

cleaned = re.sub(r'\s+', ' ', cleaned).strip()
print(f'Step 8 - Final cleaned: {repr(cleaned)}')

# Check conditions
words = cleaned.split()
print(f'Word count: {len(words)} (need >= 5)')

ends_properly = cleaned.endswith(('.', '!', '?', ':', ';', '"', "'", ')', ']', '}'))
print(f'Ends properly: {ends_properly}')

has_keywords = bool(re.search(r'\b(the|a|an|is|are|was|were|have|has|will|can|should|would)\b', cleaned.lower()))
print(f'Has keywords: {has_keywords}')
print(f'Keywords found: {re.findall(r"\\b(the|a|an|is|are|was|were|have|has|will|can|should|would)\\b", cleaned.lower())}')

should_trigger = len(words) >= 5 and not ends_properly and has_keywords
print(f'Should trigger period rule: {should_trigger}')

# Actually test
result = check_period_placement(text)
print(f'Actual result: {len(result)} suggestions')
if result:
    for r in result:
        print(f'  Suggestion: {r["message"]}')
