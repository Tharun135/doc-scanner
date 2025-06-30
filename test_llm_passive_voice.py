#!/usr/bin/env python3
"""
Test the enhanced LLM-based passive voice conversion with the user's specific example.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import app.rules.passive_voice as passive_voice

def test_user_specific_example():
    """Test the specific sentence that was causing issues."""
    
    print("=== Testing User's Specific Example ===\n")
    
    user_sentence = "This tool is needed to convert vendor and device specific configuration files to the standardized Connectivity-Suite compatible configurations."
    
    print(f"Input: {user_sentence}")
    print("-" * 80)
    
    suggestions = passive_voice.check(user_sentence)
    
    if suggestions:
        print("Generated suggestion:")
        print(suggestions[0])
    else:
        print("No passive voice detected")
    
    print("\n" + "="*80)
    
    # Test some other problematic patterns
    other_test_cases = [
        "The file is required to complete the process.",
        "Settings are configured automatically by the system.",
        "The application was developed by our team.",
        "This feature is used to enhance performance."
    ]
    
    print("\nTesting other passive voice patterns:")
    print("="*50)
    
    for i, test_case in enumerate(other_test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        suggestions = passive_voice.check(test_case)
        if suggestions:
            # Extract just the AI suggestion part
            suggestion_text = suggestions[0]
            lines = suggestion_text.split('\n')
            for line in lines:
                if line.startswith('AI suggestion:'):
                    print(f"AI suggestion: {line.replace('AI suggestion:', '').strip()}")
                    break
        else:
            print("No passive voice detected")

if __name__ == "__main__":
    test_user_specific_example()
