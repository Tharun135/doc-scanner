#!/usr/bin/env python3
"""
Test the grammar issues rule that clearly identifies problems.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_grammar_issues():
    """Test the grammar issues rule."""
    print("=" * 70)
    print("TESTING GRAMMAR ISSUES DETECTION")
    print("=" * 70)
    
    try:
        from rules.grammar_issues import check
        
        # Test cases with clear grammar issues
        test_cases = [
            {
                "title": "User's Example - Missing Hyphens",
                "content": "You need this tool to convert vendor and device specific configuration files to the standardized Connectivity-Suite compatible configurations."
            },
            {
                "title": "Subject-Verb Disagreement",
                "content": "The files is processed automatically. The systems has been updated."
            },
            {
                "title": "Unclear Pronoun Reference", 
                "content": "The system processes the data and the configuration. It should be checked regularly."
            },
            {
                "title": "More Compound Adjectives",
                "content": "This is a real time monitoring system for cross platform applications."
            },
            {
                "title": "Multiple Issues",
                "content": "The user friendly interface supports real time data processing and third party integrations."
            },
            {
                "title": "Technical Examples",
                "content": "Configure the multi user environment for high performance computing tasks."
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'-' * 60}")
            print(f"TEST {i}: {test_case['title']}")
            print(f"{'-' * 60}")
            print(f"Content: {test_case['content']}")
            print("\nGrammar Issues Detected:")
            
            suggestions = check(test_case['content'])
            
            if suggestions:
                for j, suggestion in enumerate(suggestions, 1):
                    # Extract just the issue description
                    lines = suggestion.split('\n')
                    issue_line = lines[0].replace('Issue: ', '')
                    print(f"{j}. {issue_line}")
                    
                    # Show the specific advice
                    advice_line = next((line for line in lines if 'AI suggestion:' in line), '')
                    if advice_line:
                        advice = advice_line.replace('AI suggestion: ', '')
                        print(f"   → {advice}")
                    print()
            else:
                print("No grammar issues detected.")
        
        print("\n" + "=" * 70)
        print("GRAMMAR ISSUES TEST COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grammar_issues()
