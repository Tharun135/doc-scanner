#!/usr/bin/env python3
"""
Final test to demonstrate the solution for the runtime issue.
"""

import sys
import os

# Add paths
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
rules_dir = os.path.join(app_dir, 'rules')
sys.path.insert(0, app_dir)
sys.path.insert(0, rules_dir)

def test_runtime_issue():
    """Test the original issue with 'runtime' being flagged as misspelled."""
    
    print("=== Testing Custom Terminology Solution ===")
    print()
    
    # Test terminology management
    from simple_terminology import is_custom_whitelisted
    print("1. Testing terminology whitelist:")
    print(f"   'runtime' is whitelisted: {is_custom_whitelisted('runtime')}")
    print(f"   'untie' is whitelisted: {is_custom_whitelisted('untie')}")
    print()
    
    # Test the original problematic text
    original_text = "WinCC Unified Runtime app supports the configuration"
    print(f"2. Testing original text: '{original_text}'")
    
    try:
        from spelling_checker import check
        suggestions = check(original_text)
        
        print(f"   Spelling suggestions found: {len(suggestions)}")
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"     {i}. {suggestion}")
        else:
            print("   ✓ No spelling issues - 'runtime' correctly ignored!")
        print()
        
        # Test with actual misspellings
        print("3. Testing with actual misspellings:")
        test_cases = [
            ("Runtime is working correctly", "Should find no issues"),
            ("The runtyme is broken", "Should catch 'runtyme' → 'runtime'"),
            ("WinCC is operationl", "Should catch 'operationl' → 'operational'"),
            ("Configuraton settings", "Should catch 'configuraton' → 'configuration'")
        ]
        
        for text, expected in test_cases:
            print(f"   Text: '{text}'")
            print(f"   Expected: {expected}")
            suggestions = check(text)
            if suggestions:
                print(f"   Found {len(suggestions)} issues:")
                for suggestion in suggestions:
                    print(f"     - {suggestion}")
            else:
                print("   ✓ No issues found")
            print()
            
    except Exception as e:
        print(f"Error during spell check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_runtime_issue()
