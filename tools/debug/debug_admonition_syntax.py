#!/usr/bin/env python3
"""
Test to identify the exact issue with markdown admonition syntax
"""

import sys
import os
sys.path.append('.')

# Test content with markdown admonition that's causing the issue
test_content = '''
<p>This is regular content.</p>
<p>!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.</p>
<p>This  has  multiple  spaces.</p>
'''

print("🔍 Testing markdown admonition syntax detection...")

# Test the grammar rule directly
from app.rules.grammar_rules import check as grammar_check
results = grammar_check(test_content)

print(f"📊 Grammar rule results: {len(results)} issues")
for i, result in enumerate(results, 1):
    print(f"  {i}. {result}")

# Check specifically for multiple spaces pattern
import re
from bs4 import BeautifulSoup
soup = BeautifulSoup(test_content, "html.parser")
text_content = soup.get_text()

print(f"\n📄 Extracted text:")
print(f"'{text_content}'")

print(f"\n🔍 Multiple spaces pattern analysis:")
matches = list(re.finditer(r"\s{2,}", text_content))
print(f"Found {len(matches)} matches:")
for i, match in enumerate(matches, 1):
    start, end = match.span()
    context_start = max(0, start - 10)
    context_end = min(len(text_content), end + 10)
    context = text_content[context_start:context_end]
    print(f"  {i}. Position {start}-{end}: '{context}' (matched: '{match.group()}')")

# Test each line separately
lines = text_content.split('\n')
print(f"\n📝 Line-by-line analysis:")
for i, line in enumerate(lines, 1):
    if line.strip():
        matches = re.findall(r"\s{2,}", line)
        print(f"  Line {i}: '{line.strip()}' -> {len(matches)} matches")
        if matches:
            print(f"    Matches: {matches}")

print(f"\n✅ Expected: The admonition syntax should be excluded, only real multiple spaces flagged")
