#!/usr/bin/env python3
"""
Test that readability rule is now disabled
"""

import sys
import os
sys.path.append('.')

# Test content that would trigger high grade level
test_content = '''
<h2>System Configuration</h2>
<p>The implementation requires comprehensive understanding of complex algorithmic methodologies and sophisticated technological infrastructures that necessitate extensive documentation and meticulous configuration procedures to ensure optimal performance characteristics.</p>
'''

print("🔍 Testing that readability rule is disabled...")

# Test using the app's load_rules function
from app.app import load_rules
rules = load_rules()

print(f"📊 Total rules loaded: {len(rules)}")
print("📝 Rule names:")
for i, rule in enumerate(rules, 1):
    rule_name = rule.__module__.split('.')[-1]
    print(f"  {i}. {rule_name}")

# Test with content that has high grade level
print(f"\n📄 Testing content with complex language...")
total_issues = 0
for rule in rules:
    rule_name = rule.__module__.split('.')[-1]
    suggestions = rule(test_content)
    issue_count = len(suggestions) if suggestions else 0
    total_issues += issue_count
    
    if issue_count > 0:
        print(f"  {rule_name}: {issue_count} issues")
        for suggestion in suggestions:
            if 'grade level' in suggestion.lower():
                print(f"    ⚠️ Found grade level issue: {suggestion}")
            else:
                print(f"    • {suggestion[:80]}...")

print(f"\n📊 Total issues found: {total_issues}")
print("✅ If no 'High grade level' issues are shown above, the rule is successfully disabled!")
