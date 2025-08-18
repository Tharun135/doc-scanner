#!/usr/bin/env python3
"""
Debug the regex pattern for 'open' verb
"""

import re

def debug_open_regex():
    """Debug the regex pattern for open verb."""
    
    # This is the pattern from your rule
    pattern = r'\bopens?\b'
    
    test_strings = [
        "The user opens the dialog window.",
        "Open the dialog window.", 
        "First, the user Opens the application.",
        "The application opens automatically."
    ]
    
    print("🔍 Debugging 'opens?' Regex Pattern")
    print("=" * 45)
    print(f"Pattern: {pattern}")
    print()
    
    for test_string in test_strings:
        print(f"📝 Test: '{test_string}'")
        
        # Test the regex
        match = re.search(pattern, test_string, re.IGNORECASE)
        if match:
            found_verb = match.group()
            print(f"   ✅ Match found: '{found_verb}'")
            print(f"   📍 Position: {match.start()}-{match.end()}")
            
            # Test the comparison logic
            replacement = 'Open'
            if found_verb.lower() != replacement.lower():
                print(f"   🎯 Would suggest: '{replacement}' instead of '{found_verb}'")
            else:
                print(f"   ⚪ No suggestion needed: '{found_verb}' vs '{replacement}'")
        else:
            print(f"   ❌ No match found")
        print()

if __name__ == "__main__":
    debug_open_regex()
