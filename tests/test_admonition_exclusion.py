#!/usr/bin/env python3
"""
Test that markdown admonition syntax is excluded from multiple spaces check
"""

import sys
import os
sys.path.append('.')

# Test different scenarios
test_cases = [
    # Case 1: Just admonition (should be ignored)
    {
        "name": "Admonition only",
        "content": '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.',
        "expected_issues": 0
    },
    # Case 2: Admonition + real multiple spaces (should flag only the real spaces)
    {
        "name": "Admonition + real spaces", 
        "content": '''!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.
This  sentence  has  multiple  spaces.''',
        "expected_issues": 1
    },
    # Case 3: Just multiple spaces (should be flagged)
    {
        "name": "Only multiple spaces",
        "content": 'This  sentence  has  multiple  spaces.',
        "expected_issues": 1
    },
    # Case 4: No issues (should be clean)
    {
        "name": "Clean content",
        "content": '''!!! info "NOTICE" These values are derived.
This sentence has no extra spaces.''',
        "expected_issues": 0
    }
]

print("🔍 Testing markdown admonition exclusion from multiple spaces check...")

from app.rules.grammar_rules import check as grammar_check

for i, test_case in enumerate(test_cases, 1):
    print(f"\n📝 Case {i}: {test_case['name']}")
    print(f"Content: {test_case['content'][:60]}...")
    
    results = grammar_check(f"<p>{test_case['content']}</p>")
    spaces_issues = [r for r in results if 'consecutive spaces' in r]
    
    print(f"Expected: {test_case['expected_issues']} spaces issues")
    print(f"Found: {len(spaces_issues)} spaces issues")
    
    if len(spaces_issues) == test_case['expected_issues']:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        for issue in spaces_issues:
            print(f"    • {issue}")

print(f"\n✅ Expected: Admonition syntax ignored, only real multiple spaces flagged")
