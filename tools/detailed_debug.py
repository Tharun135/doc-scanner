#!/usr/bin/env python3

import sys
sys.path.append('.')
import re

from app.rules.grammar_rules import check

# Test with the exact content, checking for hidden characters
test_content = '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.'

print("=== CHARACTER ANALYSIS ===")
print(f"Content length: {len(test_content)}")
print(f"Content repr: {repr(test_content)}")
print()

# Show each character with its ASCII code
print("Character breakdown:")
for i, char in enumerate(test_content):
    if char == ' ':
        print(f"{i:2d}: SPACE (32)")
    elif char == '\t':
        print(f"{i:2d}: TAB (9)")
    elif char == '\n':
        print(f"{i:2d}: NEWLINE (10)")
    elif char == '\r':
        print(f"{i:2d}: CARRIAGE RETURN (13)")
    else:
        print(f"{i:2d}: '{char}' ({ord(char)})")

print("\n=== SPACE ANALYSIS ===")
# Look for multiple consecutive spaces specifically
space_pattern = r'[ \t]{2,}'
spaces = list(re.finditer(space_pattern, test_content))
print(f"Multiple spaces found: {len(spaces)}")
for match in spaces:
    start, end = match.span()
    print(f"  Position {start}-{end}: {repr(match.group())}")

# Look for any whitespace sequences
all_whitespace = r'\s{2,}'
whitespaces = list(re.finditer(all_whitespace, test_content))
print(f"Multiple whitespace found: {len(whitespaces)}")
for match in whitespaces:
    start, end = match.span()
    print(f"  Position {start}-{end}: {repr(match.group())}")

print("\n=== RULE TEST ===")
results = check(test_content)
print(f"Grammar rule results: {len(results)} suggestions")
for suggestion in results:
    print(f"  - {suggestion}")

# Test with various potential variations
print("\n=== TESTING VARIATIONS ===")
variations = [
    '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.',
    '!!! info "NOTICE"  These values are derived during the XSLT Transformation step in Model Maker.',  # double space after NOTICE"
    '!!! info  "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.',  # double space before "NOTICE"
    '!!!  info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.',  # double space after !!!
]

for i, variation in enumerate(variations, 1):
    print(f"\nVariation {i}: {repr(variation)}")
    results = check(variation)
    print(f"  Results: {len(results)} suggestions")
    for suggestion in results:
        print(f"    - {suggestion}")
