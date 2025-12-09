#!/usr/bin/env python3

# Test with the exact text that's still being flagged
import sys
sys.path.append('.')

from app.rules.grammar_rules import check

# Test with the exact content that's still being flagged
test_content = '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.'

print("Testing exact content:")
print(f"Content: {repr(test_content)}")
print()

results = check(test_content)

print(f"Found {len(results)} suggestions:")
for suggestion in results:
    print(f"- {suggestion}")

# Let's also check what the regex pattern is matching
import re

print("\nDebugging regex patterns:")
print(f"Original content: {repr(test_content)}")

# Test the current pattern
pattern = r'^\s*!!!\s+\w+(?:\s+"[^"]*")?\s*.*$'
matches = re.findall(pattern, test_content, flags=re.MULTILINE)
print(f"Admonition pattern matches: {matches}")

# Test for multiple spaces
spaces_pattern = r"\s{2,}"
space_matches = re.findall(spaces_pattern, test_content)
print(f"Multiple spaces found: {space_matches}")

# Test the substitution
text_after_sub = re.sub(pattern, '', test_content, flags=re.MULTILINE)
print(f"Text after substitution: {repr(text_after_sub)}")

remaining_spaces = re.findall(spaces_pattern, text_after_sub)
print(f"Remaining spaces after substitution: {remaining_spaces}")
