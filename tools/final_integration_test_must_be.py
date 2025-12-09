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
    alternatives = get_passive_voice_alternatives(test_sentence)
    
    if alternatives:
        print(f"\nSUCCESS: Generated {len(alternatives)} alternatives:")
        for i, alt in enumerate(alternatives, 1):
            print(f"{i}. {alt}")
    else:
        print("\nFAILED: No alternatives generated")
    
    # Test with some other modal passive examples
    test_cases = [
        "Requirements must be met before proceeding.",
        "Standards must be met for approval.", 
        "All conditions must be met.",
        "These criteria must be met:"
    ]
    
    print("\n" + "="*50)
    print("Testing additional modal passive cases:")
    
    for case in test_cases:
        print(f"\nTesting: {case}")
        alts = get_passive_voice_alternatives(case)
        if alts:
            print(f"✓ Generated {len(alts)} alternatives:")
            for alt in alts[:2]:  # Show first 2
                print(f"  - {alt}")
        else:
            print("✗ No alternatives generated")

if __name__ == "__main__":
    test_main_integration()
