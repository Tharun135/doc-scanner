#!/usr/bin/env python3
"""
Test the 'open' verb specifically to check for issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_open_verb():
    """Test the 'open' verb specifically."""
    try:
        from app.rules.rewriting_suggestions import check
        
        test_cases = [
            # Test case 1: Third person singular 'opens'
            "The user opens the dialog window.",
            
            # Test case 2: Already imperative 'open'
            "Open the dialog window.",
            
            # Test case 3: Capitalized 'Opens'
            "First, the user Opens the application.",
            
            # Test case 4: Mixed with other verbs
            "The user opens the menu and selects an option."
        ]
        
        print("🧪 Testing 'Open' Verb Detection")
        print("=" * 40)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case}")
            
            suggestions = check(test_case)
            open_suggestions = [s for s in suggestions if 'Open' in s.get('message', '')]
            
            print(f"   ✅ Found {len(open_suggestions)} 'open' suggestions:")
            for suggestion in open_suggestions:
                message = suggestion.get('message', '')
                print(f"      • {message}")
                
                # Check for the specific issue pattern
                if "'Open' instead of 'Open'" in message:
                    print(f"      ❌ FOUND THE ISSUE: {message}")
            
            if not open_suggestions:
                print(f"   ℹ️ No 'open' suggestions")
        
        print(f"\n🎉 'Open' verb test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_open_verb()
