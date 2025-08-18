#!/usr/bin/env python3

"""
Test to verify the instructional content rule has been removed.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from rules.rewriting_suggestions import check

def test_instructional_rule_removal():
    """Test that the instructional content rule no longer triggers."""
    
    # This content should have triggered the rule before removal
    test_content = """
    To access the system, click on the login button and enter your credentials. 
    Select the appropriate role from the dropdown menu. Navigate to the settings 
    page and configure your preferences. Choose the appropriate options and press save.
    """
    
    print("Testing content that would have triggered the instructional rule:")
    print(f"Content: {test_content.strip()}")
    print()
    
    # Get suggestions from the rule
    suggestions = check(test_content)
    
    print(f"Number of suggestions returned: {len(suggestions)}")
    
    # Check if any suggestions contain the removed message
    instructional_suggestions = [
        s for s in suggestions 
        if isinstance(s, dict) and 
        'message' in s and 
        ('instructional content' in s['message'].lower() or
         'numbered steps' in s['message'].lower())
    ]
    
    if instructional_suggestions:
        print("❌ FAILED: Instructional content rule was not properly removed!")
        for suggestion in instructional_suggestions:
            print(f"  Found: {suggestion['message']}")
    else:
        print("✅ SUCCESS: The instructional content rule has been removed!")
        
    if suggestions:
        print(f"\nOther suggestions still active:")
        for i, suggestion in enumerate(suggestions, 1):
            if isinstance(suggestion, dict) and 'message' in suggestion:
                print(f"  {i}. {suggestion['message']}")
            else:
                print(f"  {i}. {suggestion}")
    else:
        print("\nNo suggestions returned at all.")

if __name__ == "__main__":
    test_instructional_rule_removal()
