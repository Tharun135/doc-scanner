#!/usr/bin/env python3
"""
Test the fixed rewriting suggestions rule format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_fixed_rule():
    """Test the rule with the corrected output format."""
    try:
        from app.rules.rewriting_suggestions import check
        
        # Test case with action verbs
        test_text = "The user clicks on the button and selects the option."
        
        print("🧪 Testing Fixed Rewriting Suggestions Rule")
        print("=" * 55)
        print(f"📝 Test Input: {test_text}")
        
        suggestions = check(test_text)
        
        print(f"\n✅ Result: Found {len(suggestions)} suggestions")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. Suggestion:")
            if isinstance(suggestion, dict):
                print(f"   Text: {suggestion.get('text', 'N/A')}")
                print(f"   Start: {suggestion.get('start', 'N/A')}")
                print(f"   End: {suggestion.get('end', 'N/A')}")
                print(f"   Message: {suggestion.get('message', 'N/A')}")
                
                # Check if it has the required fields
                required_fields = ['text', 'start', 'end', 'message']
                has_all_fields = all(field in suggestion for field in required_fields)
                print(f"   ✅ Proper format: {has_all_fields}")
            else:
                print(f"   ❌ Unexpected format: {type(suggestion)} - {suggestion}")
        
        print(f"\n🎉 Rule test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_rule()
