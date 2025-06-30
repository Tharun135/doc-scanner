#!/usr/bin/env python3
"""
Comprehensive test for repeated words rule with various word types.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_comprehensive_repeated_words():
    """Test the repeated words rule with various types of words."""
    print("=" * 70)
    print("COMPREHENSIVE REPEATED WORDS TEST")
    print("=" * 70)
    
    try:
        from rules.repeated_words import check
        
        # Test cases with different types of repeated words
        test_cases = [
            {
                "category": "Modal Verbs",
                "content": "Users can can access the system. You should should configure the settings. The system will will process data."
            },
            {
                "category": "Articles & Prepositions", 
                "content": "The the system is running. Put it in in the folder. Move to to the next step."
            },
            {
                "category": "Pronouns",
                "content": "This this configuration is correct. It it works properly. You you need to check."
            },
            {
                "category": "Verbs",
                "content": "Click click the button. Save save your work. Run run the application."
            },
            {
                "category": "Nouns",
                "content": "The file file is corrupted. Check the data data integrity. Update the system system configuration."
            },
            {
                "category": "Adjectives",
                "content": "This is very important important information. The new new feature is available. Use the best best practices."
            },
            {
                "category": "Adverbs",
                "content": "Process data quickly quickly. Update settings automatically automatically. Check regularly regularly for updates."
            },
            {
                "category": "Technical Terms",
                "content": "Configure the database database connection. Update the API API endpoints. Check the server server status."
            },
            {
                "category": "Mixed Case",
                "content": "The System System is running. Check the Data Data files. Update The The configuration."
            },
            {
                "category": "Complex Sentence",
                "content": "When the the system processes data, it it automatically saves the the results to to the database database for future reference."
            },
            {
                "category": "Should NOT detect (intentional)",
                "content": "This is very very important. The process is so so slow. No no, that's not right."
            },
            {
                "category": "Edge Cases",
                "content": "Set up up the system. Log in in to access. Back up up your data regularly."
            }
        ]
        
        total_detected = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'-' * 50}")
            print(f"TEST {i}: {test_case['category']}")
            print(f"{'-' * 50}")
            print(f"Content: {test_case['content']}")
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
        print(f"COMPREHENSIVE TEST COMPLETE")
        print(f"Total repeated words detected: {total_detected}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_comprehensive_repeated_words()
