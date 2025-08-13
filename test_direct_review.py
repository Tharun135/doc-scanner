#!/usr/bin/env python3
"""Direct test of review_document with the same content"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import get_rules, review_document

# Same content as the web test
test_content = """
The document was written. It was reviewed by the team. The process will be finalized soon.
This is a very long sentence that contains redundant phrases that make it wordy and difficult to read which is problematic for clarity.
The utilization of complex terminology makes the document harder to understand.
There are mistakes in spelling and grammar that need fixing.
In order to make use of the system, you should perform an analysis and conduct a review.
The user can click on the button to access the file.
"""

print("Direct test of review_document function...")
print("=" * 60)
print(f"Content to analyze:\n{test_content.strip()}")
print("=" * 60)

try:
    rules = get_rules()
    print(f"Loaded {len(rules)} rules")
    
    result = review_document(test_content, rules)
    issues = result.get('issues', [])
    
    print(f"\nTotal issues found: {len(issues)}")
    
    if issues:
        print("\nIssues detected:")
        for i, issue in enumerate(issues):
            message = issue.get('message', 'No message')
            print(f"{i+1}. {message}")
    else:
        print("\nNo issues detected!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
