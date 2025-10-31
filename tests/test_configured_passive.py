#!/usr/bin/env python3
"""Test for 'are configured' passive voice pattern."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_passive_voice_ai import get_passive_voice_alternatives

def test_configured_passive():
    """Test the 'are configured' passive voice case."""
    print("Testing 'are configured' passive voice pattern...")
    
    test_sentence = "Configured data sources- displays the number of data sources that are configured to OPC UA Connector."
    
    print(f"\nOriginal: {test_sentence}")
    
    # Test with main production function
    result = get_passive_voice_alternatives(test_sentence)
    
    print(f"\nResult type: {type(result)}")
    
    if isinstance(result, dict) and 'suggestions' in result:
        suggestions = result['suggestions']
        print(f"\nGenerated {len(suggestions)} alternatives:")
        for i, suggestion in enumerate(suggestions, 1):
            text = suggestion['text']
            source = suggestion.get('source', 'unknown')
            print(f"{i}. {text}")
            print(f"   Source: {source}")
        
        if result.get('detected_patterns'):
            print(f"\nDetected patterns:")
            for pattern in result['detected_patterns']:
                print(f"   - {pattern['pattern']}")
        else:
            print("\nNo patterns detected!")
    else:
        print(f"\nUnexpected result: {result}")

if __name__ == "__main__":
    test_configured_passive()
