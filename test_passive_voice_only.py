#!/usr/bin/env python3
"""
Test passive voice detection specifically to see if it's working after the fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the passive voice rule directly
from app.rules.passive_voice import check

def test_passive_voice():
    print("🔧 Testing passive voice detection specifically...")
    
    # Test texts with obvious passive voice
    test_texts = [
        "The document was written by the team.",
        "The report was reviewed by management.",
        "Mistakes were made during the process.",
        "The system is being updated by IT.",
        "The code was reviewed.",
        "Active voice sentence works fine.",
        "We write documents clearly."
    ]
    
    for text in test_texts:
        print(f"\n📄 Testing: '{text}'")
        try:
            result = check(text)
            if result:
                print(f"✅ Found {len(result)} passive voice issues:")
                for issue in result:
                    print(f"   - {issue}")
            else:
                print("➖ No passive voice detected")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_passive_voice()
