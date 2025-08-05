#!/usr/bin/env python3
"""
Simple test for rewriting suggestions rule
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_rule():
    """Test the rewriting suggestions rule directly."""
    try:
        from app.rules.rewriting_suggestions import check
        
        # Test case: Action verbs that should be converted
        test_text = "The user clicks on the button and selects the option. Then types the information."
        
        print("🧪 Testing Rewriting Suggestions Rule")
        print("=" * 50)
        print(f"📝 Test Input: {test_text}")
        
        suggestions = check(test_text)
        
        print(f"\n✅ Result: Found {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions, 1):
            if isinstance(suggestion, dict):
                print(f"{i}. Type: {suggestion.get('type', 'unknown')}")
                print(f"   Message: {suggestion.get('message', 'No message')}")
                print(f"   Suggestion: {suggestion.get('suggestion', 'No suggestion')}")
            else:
                print(f"{i}. {suggestion}")
        
        if not suggestions:
            print("   ℹ️ No suggestions found - rule may need adjustment")
            
        print(f"\n🎉 Rule test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rule()
