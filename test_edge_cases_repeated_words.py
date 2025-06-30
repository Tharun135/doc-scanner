#!/usr/bin/env python3
"""
Test edge cases and special scenarios for repeated words rule.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_edge_cases():
    """Test edge cases for the repeated words rule."""
    print("=" * 70)
    print("REPEATED WORDS RULE - EDGE CASES TEST")
    print("=" * 70)
    
    try:
        from rules.repeated_words import check
        
        # Test edge cases
        test_cases = [
            {
                "category": "Numbers and Alphanumeric",
                "content": "Version 2.1 2.1 is available. Use API key123 key123 for access. Set timeout to 30 30 seconds."
            },
            {
                "category": "Punctuation Separated",
                "content": "Check the file, file again. Save it; it should work. Use the API: API documentation."
            },
            {
                "category": "Line Breaks",
                "content": "Process the data\ndata carefully. Update the\nsystem system configuration."
            },
            {
                "category": "With Special Characters",
                "content": "Use @username @username for login. Set #tag #tag for categorization. Check $price $price value."
            },
            {
                "category": "Contractions",
                "content": "It's It's working properly. Don't Don't forget to save. You're You're ready to proceed."
            },
            {
                "category": "Single Letters (should skip)",
                "content": "Point A A is marked. Section B B needs review. Option C C is selected."
            },
            {
                "category": "Very Short Words",
                "content": "Go go to the next page. Do do this task. Be be careful with settings."
            },
            {
                "category": "Hyphenated Words",
                "content": "Use well-known well-known methods. Check real-time real-time data. Apply user-friendly user-friendly design."
            },
            {
                "category": "URLs and Paths (realistic scenario)",
                "content": "Navigate to /path/to /path/to the file. Check http://example.com http://example.com for details."
            },
            {
                "category": "Multiple Spaces",
                "content": "The  system   system  is running. Check   data    data   integrity."
            }
        ]
        
        total_detected = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'-' * 50}")
            print(f"TEST {i}: {test_case['category']}")
            print(f"{'-' * 50}")
            print(f"Content: {repr(test_case['content'])}")  # Show exact content including spaces/newlines
            print("\nRepeated Words Detected:")
            
            suggestions = check(test_case['content'])
            
            if suggestions:
                for j, suggestion in enumerate(suggestions, 1):
                    # Extract just the duplicate word from the suggestion
                    lines = suggestion.split('\n')
                    issue_line = next((line for line in lines if 'Remove the duplicate' in line), '')
                    print(f"{j}. {issue_line}")
                    total_detected += 1
            else:
                print("No repeated words detected.")
        
        print(f"\n" + "=" * 70)
        print(f"EDGE CASES TEST COMPLETE")
        print(f"Total repeated words detected: {total_detected}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_edge_cases()
