#!/usr/bin/env python3
"""
Test the fix for the "types" vs "Enter" issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.rewriting_suggestions import check

def test_types_noun_usage():
    """Test that 'types' as a noun doesn't get flagged for conversion to 'Enter'"""
    
    # Test case: "types of projects" should NOT be flagged
    test_content = "WinCC Unified Runtime app supports the configuration and operation of two different types of projects:"
    
    suggestions = check(test_content)
    
    print(f"Test content: {test_content}")
    print(f"Number of suggestions: {len(suggestions)}")
    
    # Check if any suggestion mentions converting "types" to "Enter"
    types_to_enter_suggestions = [s for s in suggestions if 'types' in s.get('message', '').lower() and 'enter' in s.get('message', '').lower()]
    
    if types_to_enter_suggestions:
        print("❌ FAILED: Still getting incorrect 'types' to 'Enter' suggestions:")
        for suggestion in types_to_enter_suggestions:
            print(f"  - {suggestion.get('message', '')}")
        return False
    else:
        print("✅ PASSED: No incorrect 'types' to 'Enter' suggestions found")
        return True

def test_types_verb_usage():
    """Test that 'types' as a verb (typing action) should still be flagged"""
    
    # Test case: "types text" should be flagged for conversion to "Enter"
    test_content = "The user types the password in the field to authenticate."
    
    suggestions = check(test_content)
    
    print(f"\nTest content: {test_content}")
    print(f"Number of suggestions: {len(suggestions)}")
    
    # Check if there's a suggestion to convert "types" to "Enter" 
    types_to_enter_suggestions = [s for s in suggestions if 'types' in s.get('message', '').lower() and 'enter' in s.get('message', '').lower()]
    
    if types_to_enter_suggestions:
        print("✅ PASSED: Correctly suggesting 'types' to 'Enter' for verb usage:")
        for suggestion in types_to_enter_suggestions:
            print(f"  - {suggestion.get('message', '')}")
        return True
    else:
        print("❌ FAILED: Should suggest converting 'types' to 'Enter' for verb usage")
        return False

if __name__ == "__main__":
    print("Testing the 'types' vs 'Enter' fix...")
    
    test1_passed = test_types_noun_usage()
    test2_passed = test_types_verb_usage()
    
    print(f"\n{'='*50}")
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
    else:
        print("❌ Some tests failed. The fix needs more work.")
        sys.exit(1)
