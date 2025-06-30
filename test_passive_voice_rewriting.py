#!/usr/bin/env python3
"""
Test script to verify the enhanced passive voice detection and rewriting.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import app.rules.passive_voice as passive_voice

def test_passive_voice_rewriting():
    """Test the enhanced passive voice rewriting functionality."""
    
    print("=== Testing Enhanced Passive Voice Detection & Rewriting ===\n")
    
    # Test cases with passive voice that should be rewritten
    test_cases = [
        "The original program for the Rockwell PLC has been exported.",
        "The documentation was written by the team.",
        "The system was configured by the administrator.",
        "The application has been developed by our engineers.",
        "The report was generated automatically.",
        "The tests were executed successfully.",
        "The file was created yesterday.",
        "Settings were modified by the user."
    ]
    
    for i, test_sentence in enumerate(test_cases, 1):
        print(f"Test {i}: {test_sentence}")
        print("-" * 60)
        
        suggestions = passive_voice.check(test_sentence)
        
        if suggestions:
            for suggestion in suggestions:
                print(suggestion)
        else:
            print("No passive voice detected")
        
        print("\n" + "="*70 + "\n")

def test_specific_example():
    """Test the specific example from the user."""
    
    print("=== Testing Specific User Example ===\n")
    
    user_example = "The original program for the Rockwell PLC has been exported."
    print(f"Input: {user_example}")
    print("-" * 50)
    
    suggestions = passive_voice.check(user_example)
    
    if suggestions:
        print(suggestions[0])
    else:
        print("No suggestions generated")

if __name__ == "__main__":
    test_passive_voice_rewriting()
    test_specific_example()
