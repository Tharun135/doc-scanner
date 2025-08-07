#!/usr/bin/env python3
"""
Test script to verify the Navigate to fix works correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.rewriting_suggestions import check

def test_navigate_patterns():
    """Test different navigate patterns to ensure the fix works."""
    
    test_cases = [
        {
            "text": "Navigate to Configuration > General in the runtime manager.",
            "expected": "No suggestions (already correct)",
            "description": "Should NOT suggest changes for 'Navigate to'"
        },
        {
            "text": "User navigates the interface to find settings.",
            "expected": "Suggest 'Navigate to' instead of 'navigates'",
            "description": "Should suggest changes for 'navigates' without 'to'"
        },
        {
            "text": "Navigate the menu to find options.",
            "expected": "Suggest 'Navigate to' instead of 'Navigate'", 
            "description": "Should suggest changes for 'Navigate' without 'to'"
        },
        {
            "text": "The user navigate to the page.",
            "expected": "Suggest 'Navigate to' instead of 'navigate'",
            "description": "Should suggest changes for 'navigate' without 's'"
        }
    ]
    
    print("Testing Navigate to fix...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input: '{test_case['text']}'")
        
        suggestions = check(test_case['text'])
        
        if suggestions:
            for suggestion in suggestions:
                if "Navigate" in suggestion['message']:
                    print(f"✓ Suggestion found: {suggestion['message']}")
                else:
                    print(f"• Other suggestion: {suggestion['message']}")
        else:
            print("✓ No suggestions (text is already correct)")
        
        print(f"Expected: {test_case['expected']}")

if __name__ == "__main__":
    test_navigate_patterns()
