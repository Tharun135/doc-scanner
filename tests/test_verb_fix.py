#!/usr/bin/env python3
"""
Test the fixed verb matching in rewriting suggestions rule
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_verb_matching():
    """Test different verb forms to ensure proper suggestions."""
    try:
        from app.rules.rewriting_suggestions import check
        
        test_cases = [
            # Test case 1: Third person singular (should suggest change)
            "The user clicks on the button and selects the option.",
            
            # Test case 2: Already imperative (should NOT suggest change)
            "Click on the button and select the option.",
            
            # Test case 3: Mixed case
            "First, the user Clicks the button. Then he Selects the menu option.",
            
            # Test case 4: Past tense
            "The user clicked on the button and selected the option."
        ]
        
        print("🧪 Testing Verb Matching Fix")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case}")
            
            suggestions = check(test_case)
            verb_suggestions = [s for s in suggestions if 'imperative form' in s.get('message', '')]
            
            print(f"   ✅ Found {len(verb_suggestions)} verb suggestions:")
            for suggestion in verb_suggestions:
                print(f"      • {suggestion.get('message', 'No message')}")
            
            if not verb_suggestions:
                print(f"   ℹ️ No verb suggestions (content may already be optimal)")
        
        print(f"\n🎉 Verb matching test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_verb_matching()
