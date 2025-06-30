#!/usr/bin/env python3
"""
Test the passive voice functionality with the specific problematic sentence.
"""

import re
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_sentence_specific():
    """Test the specific sentence that's causing issues."""
    
    # Test sentence from the user
    test_sentence = "It is utilized when a provided configuration file needs to be converted to the format used by the"
    
    print("=" * 70)
    print("TESTING SPECIFIC PASSIVE VOICE SENTENCE")
    print("=" * 70)
    print(f"Sentence: {test_sentence}")
    print()
    
    # Test pattern detection
    print("1. PATTERN DETECTION:")
    print("-" * 30)
    
    patterns_to_test = [
        r'\bit\s+is\s+utilized\b',
        r'\bneeds\s+to\s+be\s+\w+ed\b',
        r'\bused\s+by\b'
    ]
    
    for pattern in patterns_to_test:
        match = re.search(pattern, test_sentence, re.IGNORECASE)
        print(f"Pattern '{pattern}': {'✓ MATCH' if match else '✗ NO MATCH'}")
    
    print("\n2. ACTIVE VOICE CONVERSION:")
    print("-" * 30)
    
    # Test the specific rewrite patterns
    sentence_lower = test_sentence.lower()
    
    # Pattern: "It is utilized when..." -> "Use it when..."
    if re.search(r'it\s+is\s+utilized\s+when', sentence_lower):
        rewrite = re.sub(r'it\s+is\s+utilized\s+when\s+(.+)', 
                       r'Use it when \1', 
                       test_sentence, flags=re.IGNORECASE)
        print(f"✓ Rewrite successful: {rewrite}")
        
        # Format as the structured suggestion
        suggestion = f"Issue: Passive voice detected\nOriginal sentence: {test_sentence}\nAI suggestion: {rewrite}"
        print(f"\n3. FORMATTED SUGGESTION:")
        print("-" * 30)
        print(suggestion)
    else:
        print("✗ No rewrite pattern matched")

if __name__ == "__main__":
    test_sentence_specific()
