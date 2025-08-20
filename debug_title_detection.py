#!/usr/bin/env python3
"""
Debug title detection for numbered titles
"""

import sys
import os
import re
sys.path.append('.')

from app.rules.title_utils import is_title_or_heading

test_html = '''<p>1. Basic Configuration</p>'''

print("🔍 Testing title detection for numbered titles...")

# Test different variations
test_cases = [
    "1. Basic Configuration",
    "Basic Configuration", 
    "Basic Configuration\nThis regular sentence has several vague things that were written by someone and contains nominalizations like implementation.",
    "1. Basic Configuration\nThis regular sentence has several vague things that were written by someone and contains nominalizations like implementation."
]

for i, test_text in enumerate(test_cases, 1):
    is_title = is_title_or_heading(test_text, test_html)
    truncated = test_text[:50] + "..." if len(test_text) > 50 else test_text
    print(f"{i}. '{truncated}' -> Title: {is_title}")

# Test the exact problematic sentence
problematic_sentence = '''Basic Configuration
This regular sentence has several vague things that were written by someone and contains nominalizations like implementation.
'''

print(f"\n📝 Problematic sentence analysis:")
truncated_prob = problematic_sentence[:100] + "..." if len(problematic_sentence) > 100 else problematic_sentence
print(f"Text: '{truncated_prob}'")
is_title = is_title_or_heading(problematic_sentence.strip(), test_html)
print(f"Is title: {is_title}")

# Check if it matches any title patterns
text = problematic_sentence.strip()
print(f"\nPattern checks:")
numbered_match = bool(re.match(r'^\d+\.(\d+\.)*\s+[A-Z]', text))
print(f"- Numbered pattern (1. Title): {numbered_match}")

first_line = text.split('\n')[0]
print(f"- Title case of first line: {first_line.istitle()}")
print(f"- Length check: {len(text.split()) <= 8}")

config_match = bool(re.match(r'^(introduction|overview|conclusion|summary|getting started|installation|configuration)', text.lower()))
print(f"- Configuration pattern: {config_match}")

# Test just the first line
print(f"\nFirst line only: '{first_line}'")
first_line_title = is_title_or_heading(first_line, test_html)
print(f"- Is title: {first_line_title}")

first_numbered = bool(re.match(r'^\d+\.(\d+\.)*\s+[A-Z]', first_line))
print(f"- Numbered pattern: {first_numbered}")

first_config = bool(re.match(r'^(introduction|overview|conclusion|summary|getting started|installation|configuration)', first_line.lower()))
print(f"- Configuration pattern: {first_config}")
