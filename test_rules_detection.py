#!/usr/bin/env python3
"""Test rule detection to see what's working"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import get_rules, review_document

# Test content with various issues
test_content = """
The document was written. It was reviewed by the team. The process will be finalized soon.
This sentence is very long and contains redundant phrases that make it wordy and difficult to read, which is problematic for clarity and understanding of the main point.
The utilization of complex terminology makes the document harder to understand. You should utilize better words instead of utilize all the time.
There mistakes in speling and grammer that need fixing. The document was written with poor grammer.
In order to make use of the system, you should perform an analysis and conduct a review. It is important to understand that there are many issues.
The user can click on the button to access the file. Please see the attachment for more details.
The system will be updated very soon and it is possible to perform the task quite easily.
"""

print("Testing rule detection...")
print("=" * 50)

# Test the analyzer
try:
    print("Loading rules...")
    rules = get_rules()
    print(f"Loaded {len(rules)} rules")
    
    print("\nAnalyzing content...")
    result = review_document(test_content, rules)
    
    suggestions = result.get('issues', [])
    
    print(f"Total suggestions found: {len(suggestions)}")
    print("\nSuggestions:")
    
    category_count = {}
    for i, suggestion in enumerate(suggestions):
        category = suggestion.get('category', 'Unknown')
        text = suggestion.get('message', suggestion.get('suggestion', suggestion.get('feedback', 'No description')))
        category_count[category] = category_count.get(category, 0) + 1
        print(f"{i+1}. [{category}]: {text}")
        # Debug: show all suggestion details
        for key, value in suggestion.items():
            print(f"   {key}: {value}")
        print()
    
    print(f"\nCategory summary:")
    for category, count in category_count.items():
        print(f"- {category}: {count} suggestions")
    
except Exception as e:
    print(f"Error running test: {e}")
    import traceback
    traceback.print_exc()
