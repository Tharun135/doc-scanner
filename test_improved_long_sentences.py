#!/usr/bin/env python3
"""
Test script for the improved long sentence rule.
"""

import sys
import os
sys.path.append('app')

# Import the updated long sentences rule
from rules import long_sentences

def test_long_sentence_breaking():
    """Test the AI-powered sentence breaking functionality."""
    
    # Test case from user's example
    test_content = """
    The Industrial Edge Hub (IE Hub for short) is the central repository for all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem.
    """
    
    print("Testing improved long sentence rule...")
    print("=" * 60)
    
    print("Input text:")
    print(f'"{test_content.strip()}"')
    print()
    
    # Run the check
    suggestions = long_sentences.check(test_content)
    
    print("Results:")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\nSuggestion {i}:")
            print("-" * 30)
            print(suggestion)
    else:
        print("No suggestions found")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_long_sentence_breaking()
