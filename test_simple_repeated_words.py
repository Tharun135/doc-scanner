#!/usr/bin/env python3
"""
Test the repeated words rule the same way the web app uses it.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_repeated_words_web_app_style():
    """Test the repeated words rule as used by the web app."""
    print("=" * 70)
    print("TESTING REPEATED WORDS RULE - WEB APP STYLE")
    print("=" * 70)
    
    try:
        # Import the rule directly
        from rules.repeated_words import check
        
        # Test content with repeated words
        test_content = "Unlike the Tag Table Export in TIA Portal, the export using the WinCC Tag Converter can can include multiple CPUs."
        
        print(f"Testing content:")
        print(f'"{test_content}"')
        print(f"\nRule suggestions:")
        
        # Get suggestions from our rule
        suggestions = check(test_content)
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. {suggestion}")
                print(f"   Type: {type(suggestion)}")
        else:
            print("No suggestions found.")
        
        print("\n" + "=" * 70)
        print("DIRECT RULE TEST COMPLETE")
        print("=" * 70)
        
        return len(suggestions) > 0
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_repeated_words_web_app_style()
    if success:
        print("\n✓ Repeated words rule working correctly!")
    else:
        print("\n✗ Rule test failed")
