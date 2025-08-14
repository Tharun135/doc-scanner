#!/usr/bin/env python3
"""Test the fix for the choose/select rule"""

from app.app import get_rules, review_document

# Test the original case that was problematic
original_problem = """
This document explains how to configure the system.

Enable autostart to automatically start the application when the computer boots.

You can choose different options from the menu. Users should select the appropriate settings for their needs.
"""

rules = get_rules()
result = review_document(original_problem, rules)
print('Original problematic document test:')
print(f'Total issues found: {len(result.get("issues", []))}')
print()

for i, issue in enumerate(result.get('issues', [])):
    message = issue.get('message', str(issue))
    text = issue.get('text', '')
    start = issue.get('start', 0)
    end = issue.get('end', 0)
    
    print(f'Issue {i+1}: {message}')
    if text:
        print(f'  Text: "{text}" (position {start}-{end})')
    else:
        print(f'  Position: {start}-{end}')
    
    # Check if this is the problematic choose/select issue
    if 'select' in message.lower() and 'choose' in message.lower():
        print(f'  -> This is the choose/select rule')
        if text == '' and start == 0 and end == 0:
            print(f'  ❌ STILL HAS POSITION PROBLEM!')
        else:
            print(f'  ✅ Position information is correct now')
        
        # Check what text it should be pointing to
        if start > 0 and end > 0 and end <= len(original_problem):
            actual_text = original_problem[start:end]
            print(f'  Actual text at position: "{actual_text}"')
    print()

print("=" * 50)
print("SUMMARY:")
print("The original issue was that 'Enable autostart' was incorrectly")
print("flagged with 'Use select instead of choose for UI actions'.")
print()
print("After the fix:")
print("1. 'Enable autostart' should NOT be flagged (no UI context)")
print("2. 'choose different options from the menu' SHOULD be flagged (has 'menu')")
print("3. Position information should be accurate")
