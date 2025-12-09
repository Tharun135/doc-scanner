#!/usr/bin/env python3
"""
Test the exact user's original sentence.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.rewriting_suggestions import check

def test_original_sentence():
    """Test the user's exact original sentence."""
    
    original_text = """Navigate to Configuration > General in the runtime manager.
The General page appears as follows:"""
    
    print("Testing original user sentence...")
    print("=" * 50)
    print(f"Input: '{original_text}'")
    
    suggestions = check(original_text)
    
    if suggestions:
        print("❌ Found suggestions (should not have any):")
        for suggestion in suggestions:
            print(f"  • {suggestion['message']}")
    else:
        print("✅ No suggestions found - FIXED!")
        print("The system now correctly recognizes 'Navigate to' and doesn't suggest changes.")

if __name__ == "__main__":
    test_original_sentence()
