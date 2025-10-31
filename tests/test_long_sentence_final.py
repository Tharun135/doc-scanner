#!/usr/bin/env python3
"""
Test with the exact sentence that should trigger both rules originally
"""

import sys
import os
sys.path.append('.')

# Test content with the exact long sentence
test_content = '''
<p>In Model Maker, navigate to the XSLT Transformer tab, click on the Open L5X File button, and select the PLC program file exported from RSLogix 5000 or, Studio 5000 in .L5X format.</p>
'''

print("🔍 Testing long sentence detection after fix...")

# Test using the app's load_rules function
from app.app import load_rules
rules = load_rules()

print(f"📊 Total rules loaded: {len(rules)}")

# Test with the long sentence content
print(f"\n📄 Testing content with 32-word sentence...")
all_suggestions = []
for rule in rules:
    rule_name = rule.__module__.split('.')[-1]
    suggestions = rule(test_content)
    
    if suggestions:
        print(f"\n  {rule_name}: {len(suggestions)} issues")
        for suggestion in suggestions:
            print(f"    • {suggestion}")
            all_suggestions.append(suggestion)

# Check for duplicates
print(f"\n📊 Analysis:")
print(f"  - Total suggestions: {len(all_suggestions)}")

long_sentence_suggestions = [s for s in all_suggestions if 'long sentence' in s.lower() or 'breaking' in s.lower() or 'simplifying' in s.lower()]
print(f"  - Long sentence suggestions: {len(long_sentence_suggestions)}")

if len(long_sentence_suggestions) > 1:
    print("  ⚠️ DUPLICATE FOUND!")
    for i, suggestion in enumerate(long_sentence_suggestions, 1):
        print(f"    {i}. {suggestion[:80]}...")
else:
    print("  ✅ No duplicates found!")
    if long_sentence_suggestions:
        print(f"  Single suggestion: {long_sentence_suggestions[0][:100]}...")

print(f"\n✅ Expected: Only 1 long sentence suggestion instead of 2")
