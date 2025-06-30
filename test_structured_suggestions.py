#!/usr/bin/env python3
"""
Test script to verify the new structured AI suggestion format.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.rules import special_characters, can_may_terms

def test_structured_suggestions():
    """Test that suggestions now follow the structured format."""
    
    print("=== Testing Structured AI Suggestion Format ===\n")
    
    # Test cases for different rule types
    test_cases = [
        {
            "name": "Apostrophe rule (special_characters)",
            "text": "API's are important for integration.",
            "rule_module": special_characters
        },
        {
            "name": "Modal verb rule (can_may_terms)",
            "text": "You can click the button to save.",
            "rule_module": can_may_terms
        },
        {
            "name": "Ampersand rule (special_characters)",
            "text": "Use JavaScript & CSS for styling.",
            "rule_module": special_characters
        },
        {
            "name": "May usage rule (can_may_terms)",
            "text": "This may cause problems.",
            "rule_module": can_may_terms
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['text']}'")
        
        suggestions = test_case['rule_module'].check(test_case['text'])
        
        if suggestions:
            for j, suggestion in enumerate(suggestions, 1):
                print(f"\nSuggestion {j}:")
                print("-" * 50)
                print(suggestion)
                print("-" * 50)
                
                # Check if suggestion follows the structured format
                has_issue = "Issue:" in suggestion
                has_original = "Original sentence:" in suggestion
                has_ai_suggestion = "AI suggestion:" in suggestion
                
                structure_score = sum([has_issue, has_original, has_ai_suggestion])
                
                if structure_score == 3:
                    print("✅ FORMAT: Perfectly structured")
                elif structure_score >= 2:
                    print(f"⚠️  FORMAT: Partially structured ({structure_score}/3 components)")
                else:
                    print("❌ FORMAT: Not structured")
        else:
            print("No suggestions generated")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_structured_suggestions()
