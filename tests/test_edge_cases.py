#!/usr/bin/env python3
"""
Additional tests to ensure we didn't break anything
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.rewriting_suggestions import check

def test_edge_cases():
    """Test various edge cases for the types/Enter rule"""
    
    test_cases = [
        # Should NOT trigger (noun usage)
        ("There are several types of configurations available.", False),
        ("Choose from different types of authentication methods.", False),
        ("The system supports multiple types of connections.", False),
        ("Various types of errors can occur.", False),
        
        # Should trigger (verb usage in procedural context)
        ("The operator types the username into the login field.", True),
        ("User types a new password in the dialog box.", True),
        ("The technician types configuration data into the form.", True),
        
        # Edge cases
        ("Types of projects are listed in the menu.", False),  # "Types" at start, still a noun
        ("The user types.", True),  # Just "types" as verb (though may not have good context)
    ]
    
    print("Testing edge cases...\n")
    
    all_passed = True
    for i, (content, should_trigger) in enumerate(test_cases, 1):
        suggestions = check(content)
        
        # Check for types->Enter suggestions
        types_suggestions = [s for s in suggestions 
                           if 'types' in s.get('message', '').lower() 
                           and 'enter' in s.get('message', '').lower()]
        
        has_suggestion = len(types_suggestions) > 0
        
        print(f"Test {i}: {content}")
        print(f"   Expected: {'Should trigger' if should_trigger else 'Should NOT trigger'}")
        print(f"   Actual: {'Triggered' if has_suggestion else 'Did not trigger'}")
        
        if has_suggestion == should_trigger:
            print(f"   ✅ PASSED")
        else:
            print(f"   ❌ FAILED")
            all_passed = False
            
        if has_suggestion:
            print(f"   Suggestion: {types_suggestions[0].get('message', '')}")
        print()
    
    return all_passed

if __name__ == "__main__":
    success = test_edge_cases()
    
    print(f"{'='*60}")
    if success:
        print("🎉 ALL EDGE CASE TESTS PASSED!")
        print("The fix correctly handles various scenarios.")
    else:
        print("❌ Some edge case tests failed.")
        print("The fix may need further refinement.")
        sys.exit(1)
