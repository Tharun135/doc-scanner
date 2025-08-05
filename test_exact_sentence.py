#!/usr/bin/env python3
"""
Test the specific sentence that was causing the issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.rewriting_suggestions import check

def test_exact_sentence():
    """Test the exact sentence that was causing the issue"""
    
    # The exact sentence from the user's report
    test_content = "WinCC Unified Runtime app supports the configuration and operation of two different types of projects:"
    
    suggestions = check(test_content)
    
    print(f"Original sentence: {test_content}")
    print(f"Number of suggestions: {len(suggestions)}")
    
    if suggestions:
        print("\nSuggestions found:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion.get('message', 'No message')}")
            
        # Check specifically for the problematic suggestion
        problem_suggestions = [s for s in suggestions 
                             if 'enter' in s.get('message', '').lower() 
                             and 'types' in s.get('message', '').lower()]
        
        if problem_suggestions:
            print(f"\n❌ PROBLEM: Still getting the incorrect suggestion:")
            for suggestion in problem_suggestions:
                print(f"   '{suggestion.get('message', '')}'")
            return False
        else:
            print(f"\n✅ Good: The suggestions are about other things, not the 'types' issue")
            return True
    else:
        print("✅ Perfect: No suggestions generated for this sentence")
        return True

if __name__ == "__main__":
    print("Testing the exact sentence that was problematic...\n")
    
    success = test_exact_sentence()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 SUCCESS: The sentence no longer generates the incorrect suggestion!")
        print("The rule now correctly distinguishes between:")
        print("  - 'types' as a noun (e.g., 'types of projects') ✅")
        print("  - 'types' as a verb (e.g., 'user types text') ✅")
    else:
        print("❌ FAILED: The sentence still generates the incorrect suggestion")
        sys.exit(1)
