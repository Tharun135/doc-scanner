#!/usr/bin/env python3
"""Test additional navigation passive voice patterns."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_passive_voice_ai import get_passive_voice_alternatives

def test_additional_navigation():
    """Test additional navigation passive voice patterns."""
    print("🔍 Testing Additional Navigation Patterns")
    print("="*50)
    
    test_cases = [
        "You will be taken to the settings page.",
        "Users will be directed to the login screen.",
        "The user will be navigated to the dashboard.",
        "After clicking, you will be taken to the configuration menu."
    ]
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\nTest {i}: {sentence}")
        
        result = get_passive_voice_alternatives(sentence)
        
        if isinstance(result, dict) and 'suggestions' in result:
            suggestions = result['suggestions']
            if suggestions:
                print(f"✅ Generated {len(suggestions)} alternatives:")
                for j, suggestion in enumerate(suggestions[:2], 1):  # Show first 2
                    text = suggestion['text']
                    print(f"   {j}. {text}")
            else:
                print("❌ No alternatives generated")
        else:
            print(f"❌ Unexpected result: {result}")

if __name__ == "__main__":
    test_additional_navigation()
