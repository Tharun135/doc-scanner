#!/usr/bin/env python3
"""
Test script for the repeated words detection rule.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_repeated_words_rule():
    """Test the repeated words detection rule."""
    print("=" * 70)
    print("TESTING REPEATED WORDS DETECTION RULE")
    print("=" * 70)
    
    # Import the rule
    try:
        from rules.repeated_words import check
        
        # Test cases with repeated words
        test_cases = [
            {
                "title": "Original Issue - 'can can'",
                "content": "Unlike the Tag Table Export in TIA Portal, the export using the WinCC Tag Converter can can include multiple CPUs."
            },
            {
                "title": "Common repeated word - 'the the'",
                "content": "The system will automatically process the the data files when they are uploaded."
            },
            {
                "title": "Repeated 'is is'",
                "content": "This configuration is is required for proper operation of the network."
            },
            {
                "title": "Multiple repeated words",
                "content": "The user can can access the system and and modify the settings as needed."
            },
            {
                "title": "No repeated words (should be clean)",
                "content": "The Tag Table Export in TIA Portal allows you to export configuration data efficiently."
            },
            {
                "title": "Intentional repetition (should be skipped)",
                "content": "This is very very important to understand."
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'-' * 50}")
            print(f"TEST {i}: {test_case['title']}")
            print(f"{'-' * 50}")
            print(f"Content: {test_case['content']}")
            print("\nRepeated Words Detected:")
            
            suggestions = check(test_case['content'])
            
            if suggestions:
                for j, suggestion in enumerate(suggestions, 1):
                    print(f"{j}. {suggestion}")
            else:
                print("No repeated words detected.")
        
        print("\n" + "=" * 70)
        print("REPEATED WORDS RULE TEST COMPLETE")
        print("=" * 70)
        
        return True
        
    except ImportError as e:
        print(f"Error importing repeated words rule: {e}")
        return False
    except Exception as e:
        print(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    test_repeated_words_rule()
