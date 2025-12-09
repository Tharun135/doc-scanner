#!/usr/bin/env python3
"""
Test that nominalization rule is now disabled
"""

import sys
import os
sys.path.append('.')

# Test content that would trigger nominalizations
test_content = '''
<h2>System Configuration</h2>
<p>RSLogix 5000 Windows application from Rockwell Automation to open the target PLC program(s) and select File --> Save As...</p>
<p>The implementation of this solution requires careful configuration and testing.</p>
'''

print("🔍 Testing that nominalization rule is disabled...")

# Test using the app's load_rules function
from app.app import load_rules
rules = load_rules()

print(f"📊 Total rules loaded: {len(rules)}")
print("📝 Rule names:")
for i, rule in enumerate(rules, 1):
    rule_name = rule.__module__.split('.')[-1]
    print(f"  {i}. {rule_name}")

# Test with content that has nominalizations
print(f"\n📄 Testing content with nominalizations...")
total_issues = 0
for rule in rules:
    rule_name = rule.__module__.split('.')[-1]
    suggestions = rule(test_content)
    issue_count = len(suggestions) if suggestions else 0
    total_issues += issue_count
    
    if issue_count > 0:
        print(f"  {rule_name}: {issue_count} issues")
        for suggestion in suggestions:
            if 'nominalization' in suggestion.lower():
                print(f"    ⚠️ Found nominalization issue: {suggestion}")
            else:
                print(f"    • {suggestion[:80]}...")

print(f"\n📊 Total issues found: {total_issues}")
print("✅ If no nominalization issues are shown above, the rule is successfully disabled!")
