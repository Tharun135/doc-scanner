#!/usr/bin/env python3
"""Find which rule creates wrong position info"""

from app.app import get_rules, review_document

# Test just the problematic sentence to see which rule flags it
test_content = 'You can choose to set any project to Autostart mode by activating the'
rules = get_rules()
result = review_document(test_content, rules)

print('Issues for incomplete sentence:')
for issue in result.get('issues', []):
    print(f'  Issue: {issue.get("message", "")}')
    print(f'  Text: {repr(issue.get("text", ""))}')
    print(f'  Position: {issue.get("start", 0)}-{issue.get("end", 0)}')
    print(f'  Expected position should be within 0-{len(test_content)}')
    print()

print(f'Test content length: {len(test_content)}')
print(f'Test content: {repr(test_content)}')
