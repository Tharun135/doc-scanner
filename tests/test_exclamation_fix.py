#!/usr/bin/env python3
"""
Test the fixed exclamation mark detection in tone_voice rule
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_exclamation_fix():
    """Test that NOTE/NOTICE templates don't trigger excessive exclamation warnings."""
    try:
        from app.rules.tone_voice import check
        
        test_cases = [
            # Test case 1: Should NOT trigger (NOTE template)
            """
            > **NOTE**! This is important information.
            
            This is regular content with normal punctuation.
            """,
            
            # Test case 2: Should NOT trigger (NOTICE template)  
            """
            **NOTICE**! Please read this carefully.
            
            Regular content follows here.
            """,
            
            # Test case 3: Should NOT trigger (WARNING template)
            """
            > **WARNING**! This action cannot be undone.
            
            Proceed with caution.
            """,
            
            # Test case 4: Should trigger (excessive exclamation marks in regular text)
            """
            This is amazing! It's so cool! I love this feature! 
            Everything is awesome! This is the best!
            """,
            
            # Test case 5: Mixed case - template + excessive in content
            """
            > **NOTE**! Important information here.
            
            This is so cool! Amazing! Fantastic! Incredible! Awesome!
            """,
            
            # Test case 6: Should NOT trigger (single exclamation in regular content)
            """
            Click the Save button to save your work.
            Use caution when deleting files!
            """
        ]
        
        print("🧪 Testing Exclamation Mark Fix")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}:")
            print("Content:", repr(test_case.strip()[:100]) + "...")
            
            suggestions = check(test_case)
            exclamation_suggestions = [s for s in suggestions if 'exclamation marks' in s.get('message', '')]
            
            if exclamation_suggestions:
                print(f"   ⚠️ Found exclamation warnings:")
                for suggestion in exclamation_suggestions:
                    print(f"      • {suggestion.get('message', 'No message')}")
            else:
                print(f"   ✅ No exclamation warnings (good!)")
        
        print(f"\n🎉 Exclamation mark fix test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_exclamation_fix()
