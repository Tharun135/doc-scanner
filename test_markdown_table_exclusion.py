#!/usr/bin/env python3
"""
Test that markdown table syntax is excluded from long sentence rule
"""

import sys
import os
sys.path.append('.')

# Test content with markdown table that was causing the issue
test_content = '''
<h2>Configuration Table</h2>
<p>Here is the configuration information:</p>

| IE Device | Connector Configuration | IIH Essentials |
| --- | --- | --- | --- | --- | --- | --- |
| PLC | Settings for the controller | Required configuration |

<p>This is a regular sentence that should be checked if it becomes too long and contains more than twenty-five words which would trigger the long sentence rule normally.</p>
'''

print("🔍 Testing that markdown table syntax is excluded...")

# Test the long sentence rule directly
from app.rules.long_sentence import check as long_check
results = long_check(test_content)

print(f"📊 Long sentence rule results: {len(results)} issues")
for i, result in enumerate(results, 1):
    print(f"  {i}. {result}")
    
# Check if any results contain table syntax
table_issues = [r for r in results if '| --- |' in r or '|' in r and '---' in r]
if table_issues:
    print("\n⚠️ PROBLEM: Still flagging table syntax:")
    for issue in table_issues:
        print(f"    • {issue}")
else:
    print("\n✅ SUCCESS: No table syntax flagged!")

# Test with just the table separator line
print(f"\n🔍 Testing isolated table separator...")
table_only_content = '''
| --- | --- | --- | --- | --- | --- | --- |
'''

table_results = long_check(table_only_content)
print(f"📊 Table separator only: {len(table_results)} issues")
if table_results:
    print("⚠️ Still flagging table separator!")
    for r in table_results:
        print(f"    • {r}")
else:
    print("✅ Table separator correctly ignored!")

print(f"\n✅ Expected: Only the long regular sentence should be flagged, not table syntax")
