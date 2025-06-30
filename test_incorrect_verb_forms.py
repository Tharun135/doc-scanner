#!/usr/bin/env python3
"""
Test script for the incorrect verb forms detection rule.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_incorrect_verb_forms():
    """Test the incorrect verb forms detection rule."""
    print("=" * 70)
    print("TESTING INCORRECT VERB FORMS DETECTION RULE")
    print("=" * 70)
    
    # Import the rule
    try:
        from rules.incorrect_verb_forms import check
        
        # Test cases with incorrect verb forms
        test_cases = [
            {
                "title": "Original Issue - 'supporteds'",
                "content": "The user supporteds structs by providing all single elements."
            },
            {
                "title": "Original Issue - 'provideds'",
                "content": "The user provideds arrays additionally as 'array object'."
            },
            {
                "title": "Other common incorrect forms",
                "content": "The system createds new files automatically. The application updateds the database regularly."
            },
            {
                "title": "Technical verbs with -eds",
                "content": "The server processeds the data and configureds the settings. It executeds the commands successfully."
            },
            {
                "title": "Mixed correct and incorrect",
                "content": "The user supports the feature but the system supporteds additional options. The app provides data and also provideds reports."
            },
            {
                "title": "No incorrect forms (should be clean)",
                "content": "The user supports structs by providing all single elements. The system creates files and updates databases."
            },
            {
                "title": "Edge case - proper words ending in 'eds'",
                "content": "The Leeds United team played well. The seeds were planted in the garden."
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'-' * 50}")
            print(f"TEST {i}: {test_case['title']}")
            print(f"{'-' * 50}")
            print(f"Content: {test_case['content']}")
            print("\nIncorrect Verb Forms Detected:")
            
            suggestions = check(test_case['content'])
            
            if suggestions:
                for j, suggestion in enumerate(suggestions, 1):
                    # Extract the correction from the suggestion
                    lines = suggestion.split('\n')
                    correction_line = next((line for line in lines if 'Change' in line), '')
                    print(f"{j}. {correction_line}")
            else:
                print("No incorrect verb forms detected.")
        
        print("\n" + "=" * 70)
        print("INCORRECT VERB FORMS RULE TEST COMPLETE")
        print("=" * 70)
        
        return True
        
    except ImportError as e:
        print(f"Error importing incorrect verb forms rule: {e}")
        return False
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_incorrect_verb_forms()
