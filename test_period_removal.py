#!/usr/bin/env python3
"""Test that period detection has been successfully removed."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.punctuation_rules import check

def test_period_removal():
    """Test that period detection no longer triggers."""
    
    print("🧪 Testing Period Detection Removal")
    print("=" * 40)
    
    # Test content that would previously trigger period detection
    test_content = """This **bold** sentence needs a period
Check out this [documentation](https://example.com) for details
Here is an image ![screenshot](image.jpg) showing results
Use the `print()` function to display output

This sentence has proper punctuation.
This one also ends correctly!"""
    
    # Get all punctuation suggestions
    suggestions = check(test_content)
    
    # Filter for period-related suggestions
    period_suggestions = [s for s in suggestions if 'period' in s.get('message', '').lower()]
    
    print(f"Total punctuation suggestions: {len(suggestions)}")
    print(f"Period-related suggestions: {len(period_suggestions)}")
    
    if len(period_suggestions) == 0:
        print("✅ SUCCESS: Period detection has been successfully removed!")
        print("\nRemaining suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion['message']}")
    else:
        print("❌ FAILURE: Period detection is still active")
        print("\nPeriod suggestions found:")
        for i, suggestion in enumerate(period_suggestions, 1):
            print(f"  {i}. {suggestion['message']}")
    
    return len(period_suggestions) == 0

if __name__ == "__main__":
    success = test_period_removal()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Period detection rule successfully disabled!")
        print("Users will no longer see 'Consider adding period at end of sentence' issues.")
    else:
        print("⚠️  Period detection is still active. Additional steps may be needed.")
