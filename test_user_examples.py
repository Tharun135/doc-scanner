#!/usr/bin/env python3
"""
Test the exact examples provided by the user.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_user_examples():
    """Test the exact examples from the user."""
    print("=" * 70)
    print("TESTING USER'S SPECIFIC EXAMPLES")
    print("=" * 70)
    
    try:
        from rules.incorrect_verb_forms import check
        
        user_examples = [
            "The user supporteds structs by providing all single elements.",
            "The user provideds arrays additionally as \"array object\"."
        ]
        
        for i, example in enumerate(user_examples, 1):
            print(f"\nExample {i}: {example}")
            print("Suggestions:")
            
            suggestions = check(example)
            
            if suggestions:
                for j, suggestion in enumerate(suggestions, 1):
                    print(f"{j}. {suggestion}")
            else:
                print("No issues detected.")
        
        print("\n" + "=" * 70)
        print("USER EXAMPLES TEST COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_user_examples()
