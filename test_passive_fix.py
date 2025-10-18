#!/usr/bin/env python3
"""
Test script to verify the passive voice conversion for the specific LoRaWAN sentence.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from ai_improvement import AISuggestionEngine

def test_passive_conversion():
    engine = AISuggestionEngine()
    
    # Test the specific sentence that was failing
    test_sentence = "LoRaWAN tags are made available in the Databus after you have selected the corresponding option for selected tags."
    
    print("🧪 Testing Passive Voice Conversion")
    print("=" * 50)
    print(f"Original: {test_sentence}")
    
    # Test the _fix_passive_voice method directly
    converted = engine._fix_passive_voice(test_sentence)
    print(f"Converted: {converted}")
    
    # Also test the full AI suggestion
    print("\n🤖 Testing Full AI Suggestion")
    print("=" * 30)
    result = engine.generate_contextual_suggestion(
        feedback_text="Avoid passive voice in sentence",
        original_sentence=test_sentence,
        context=""
    )
    
    print(f"AI Suggestion: {result.get('suggestion', 'No suggestion')}")
    print(f"Method: {result.get('method', 'Unknown')}")
    print(f"Success: {result.get('success', False)}")
    
    # Check if the conversion actually changed the sentence
    if converted != test_sentence:
        print("\n✅ SUCCESS: Passive voice was converted!")
    else:
        print("\n❌ ISSUE: Sentence was not converted")

if __name__ == "__main__":
    test_passive_conversion()
