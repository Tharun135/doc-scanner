#!/usr/bin/env python3
"""Test to confirm period detection is disabled."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.punctuation_rules import check

test_text = '''This sentence has no period
Another sentence without punctuation  
This sentence has proper punctuation.
Check out this link for more info
Here is some **bold text** without punctuation'''

print("Testing punctuation rules with period detection disabled...")
print("=" * 60)
print(f"Test text:\n{test_text}")
print("\n" + "=" * 60)

result = check(test_text)
print(f'Found {len(result)} punctuation issues:')

for i, issue in enumerate(result, 1):
    print(f'{i}. {issue["message"]}')

# Check specifically for period-related messages
period_issues = [issue for issue in result if 'period' in issue['message'].lower()]
print(f'\nPeriod-related issues: {len(period_issues)}')

if len(period_issues) == 0:
    print("✅ SUCCESS: Period detection rule has been successfully disabled!")
else:
    print("❌ FAILURE: Period detection issues are still being generated:")
    for issue in period_issues:
        print(f"  - {issue['message']}")
