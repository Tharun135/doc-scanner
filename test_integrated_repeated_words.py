#!/usr/bin/env python3
"""
Test the integrated repeated words rule in the Doc Scanner web app context.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_integrated_repeated_words():
    """Test the repeated words rule as integrated in the web app."""
    print("=" * 70)
    print("TESTING INTEGRATED REPEATED WORDS RULE")
    print("=" * 70)
    
    try:
        # Import the app and its functions
        from app.app import load_rules, review_document
        
        # Load all rules (including our new repeated_words rule)
        rules = load_rules()
        
        print(f"Total rules loaded: {len(rules)}")
        
        # Test content with repeated words
        test_content = """
        Unlike the Tag Table Export in TIA Portal, the export using the WinCC Tag Converter can can include multiple CPUs.
        The system will automatically process the the data files when they are uploaded.
        This configuration is is required for proper operation.
        """
        
        print(f"\nTesting content:")
        print(f'"{test_content.strip()}"')
        print(f"\nSuggestions from all rules:")
        
        # Get all suggestions
        suggestions = review_document(test_content, rules)
        
        if suggestions:
            repeated_word_suggestions = []
            other_suggestions = []
            
            for suggestion in suggestions:
                if "duplicate word" in suggestion.lower() or "remove duplicate" in suggestion.lower():
                    repeated_word_suggestions.append(suggestion)
                else:
                    other_suggestions.append(suggestion)
            
            print(f"\nRepeated word suggestions ({len(repeated_word_suggestions)}):")
            for i, suggestion in enumerate(repeated_word_suggestions, 1):
                print(f"{i}. {suggestion}")
            
            if other_suggestions:
                print(f"\nOther suggestions ({len(other_suggestions)}):")
                for i, suggestion in enumerate(other_suggestions[:5], 1):  # Show only first 5
                    print(f"{i}. {suggestion}")
                if len(other_suggestions) > 5:
                    print(f"... and {len(other_suggestions) - 5} more suggestions")
        else:
            print("No suggestions found.")
        
        print("\n" + "=" * 70)
        print("INTEGRATION TEST COMPLETE")
        print("=" * 70)
        
        return len([s for s in suggestions if "duplicate word" in s.lower()]) > 0
        
    except Exception as e:
        print(f"Error during integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integrated_repeated_words()
    if success:
        print("\n✓ Repeated words rule successfully integrated!")
    else:
        print("\n✗ Integration test failed")
