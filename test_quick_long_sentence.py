#!/usr/bin/env python3
"""
Quick test to verify the long sentence rule is working correctly.
"""

import sys
import os
sys.path.append('app')

from rules import long_sentences

def test_sample_sentence():
    """Test with the user's example sentence."""
    
    test_cases = [
        "The Industrial Edge Hub (IE Hub for short) is the central repository for all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem.",
        "The comprehensive software development process includes detailed requirements analysis, thorough system design, careful implementation, extensive testing, strategic deployment, and ongoing maintenance activities that ensure quality delivery to customers.",
        "This advanced configuration file specifies the critical network parameters, security settings, authentication protocols, and comprehensive monitoring capabilities that the distributed system will use during runtime operations.",
        "The application server, which handles all incoming user requests and processes complex business logic efficiently, must be configured with appropriate memory settings and optimized connection pools for maximum throughput."
    ]
    
    print("Testing Long Sentence Rule with Multiple Examples")
    print("=" * 60)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-" * 30)
        print(f"Input: {test_text}")
        print()
        
        suggestions = long_sentences.check(test_text)
        
        if suggestions:
            for j, suggestion in enumerate(suggestions, 1):
                print(f"Suggestion {j}:")
                print(suggestion)
                print()
        else:
            print("No suggestions generated (sentence under 25 words)")
            print()

if __name__ == "__main__":
    test_sample_sentence()
