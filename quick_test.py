#!/usr/bin/env python3
"""Quick test for Enable autostart issue"""

from app.app import get_rules, review_document
import json

# Test just 'Enable autostart' to see what happens
test_content = 'Enable autostart'
rules = get_rules()
result = review_document(test_content, rules)

print('Testing: "Enable autostart"')
print('Total issues found:', len(result.get('issues', [])))
print()

if result.get('issues'):
    for i, issue in enumerate(result['issues']):
        print(f'Issue {i+1}:')
        print(f'  Message: {issue.get("message", "")}')
        print(f'  Text: "{issue.get("text", "")}"')
        print(f'  Start: {issue.get("start", "")}')
        print(f'  End: {issue.get("end", "")}')
        print()
        
        if 'select' in issue.get('message', '').lower() and 'choose' in issue.get('message', '').lower():
            print('  ⚠️ This is the problematic choose/select issue!')
else:
    print('✅ No issues detected (correct behavior)')
