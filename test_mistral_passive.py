#!/usr/bin/env python3
"""
Test script to verify Mistral 7B LLM integration for passive voice detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.passive_voice import check

def test_passive_voice_detection():
    """Test passive voice detection with Mistral 7B LLM"""
    
    # Test sentences with passive voice
    test_sentences = [
        "The document was created by the team.",
        "The system is configured automatically.",
        "Files are processed in the background.",
        "The report was generated yesterday.",
        "Passwords are required for access.",
        "The application is being tested.",
        "Data is stored securely.",
        "The configuration was updated by the administrator."
    ]
    
    print("🚀 Testing Passive Voice Detection with Mistral 7B LLM")
    print("=" * 60)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. Testing: '{sentence}'")
        suggestions = check(sentence)
        
        if suggestions:
            print(f"   ✅ Passive voice detected!")
            for j, suggestion in enumerate(suggestions, 1):
                print(f"   🔄 Suggestion {j}: {suggestion}")
        else:
            print(f"   ❌ No passive voice detected or no LLM suggestion")
    
    print("\n" + "=" * 60)
    print("✨ Test completed!")

if __name__ == "__main__":
    test_passive_voice_detection()
