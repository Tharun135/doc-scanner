#!/usr/bin/env python3
"""Final integration test for 'must be met' passive voice with main AI system."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_passive_voice_ai import get_passive_voice_alternatives

def test_main_integration():
    """Test the main integration with must be met case."""
    print("Testing main AI integration for 'must be met' passive voice...")
    
    test_sentence = "The following requirements must be met:"
    
    print(f"\nOriginal: {test_sentence}")
    
    # Test with main production function
    result = get_passive_voice_alternatives(test_sentence)
    
    print(f"Result type: {type(result)}")
    print(f"Result content: {result}")
    
    if isinstance(result, dict) and 'suggestions' in result:
        alternatives = result['suggestions']
        print(f"\nSUCCESS: Generated {len(alternatives)} alternatives:")
        for i, alt in enumerate(alternatives, 1):
            print(f"{i}. {alt}")
    elif isinstance(result, list):
        print(f"\nSUCCESS: Generated {len(result)} alternatives:")
        for i, alt in enumerate(result, 1):
            print(f"{i}. {alt}")
    else:
        print(f"\nUnexpected result format: {result}")

if __name__ == "__main__":
    test_main_integration()
