#!/usr/bin/env python3

# Debug the multiline issue
import re

# Test scenario that's failing
test_content = '''Some text before.

!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.

Some text after.'''

print("Original content:")
print(repr(test_content))
print("\nOriginal content (formatted):")
print(test_content)

# Test the current pattern
pattern = r'^\s*!!!\s+\w+(?:\s+"[^"]*")?\s*.*$'
print(f"\nPattern: {pattern}")

# Test with multiline flag
matches = re.findall(pattern, test_content, flags=re.MULTILINE)
print(f"Matches found: {matches}")

# Test the substitution
text_after_sub = re.sub(pattern, '', test_content, flags=re.MULTILINE)
print(f"\nText after first substitution:")
print(repr(text_after_sub))

# Apply the newline cleanup
text_after_cleanup = re.sub(r'\n{3,}', '\n\n', text_after_sub)
print(f"\nText after newline cleanup:")
print(repr(text_after_cleanup))

# Check for multiple spaces in the remaining text
spaces_pattern = r"\s{2,}"
space_matches = re.findall(spaces_pattern, text_after_cleanup)
print(f"\nRemaining spaces: {space_matches}")

# Let's see what specific spaces are being detected
for match in re.finditer(spaces_pattern, text_after_cleanup):
    start, end = match.span()
    print(f"Space match at {start}-{end}: {repr(text_after_cleanup[start:end])}")
    print(f"Context: {repr(text_after_cleanup[max(0,start-20):end+20])}")
