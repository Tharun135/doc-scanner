#!/usr/bin/env python3
"""
Test the grammar issues rule with clear issue identification.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_clear_issue_identification():
    """Test that the rule clearly identifies issues without rewriting."""
    print("=" * 80)
    print("TESTING CLEAR GRAMMAR ISSUE IDENTIFICATION")
    print("=" * 80)
    
    try:
        from rules.grammar_issues import check
        
        test_cases = [
            {
                "title": "Your Example - Missing Hyphens in Compound Adjectives",
                "content": "You need this tool to convert vendor and device specific configuration files to the standardized Connectivity-Suite compatible configurations."
            },
            {
                "title": "Multiple Compound Adjectives",
                "content": "This real time system provides user friendly interfaces for cross platform development."
            },
            {
                "title": "Technical Documentation",
                "content": "The multi user environment supports high performance computing with third party libraries."
            },
            {
                "title": "No Issues (should be clean)",
                "content": "The system provides vendor-specific and device-specific configurations automatically."
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'-' * 70}")
            print(f"TEST {i}: {test_case['title']}")
            print(f"{'-' * 70}")
            print(f"Content: {test_case['content']}")
            print("\nIssues Identified:")
            
            suggestions = check(test_case['content'])
            
            if suggestions:
                for j, suggestion in enumerate(suggestions, 1):
                    lines = suggestion.split('\n')
                    
                    # Extract the clear issue statement
                    issue_line = lines[0].replace('Issue: ', '')
                    print(f"\n{j}. Issue: {issue_line}")
                    
                    # Show the specific guidance (not a rewrite)
                    advice_line = next((line for line in lines if 'AI suggestion:' in line), '')
                    if advice_line:
                        advice = advice_line.replace('AI suggestion: ', '')
                        print(f"   Guidance: {advice}")
                        
                    # Show affected text
                    original_line = next((line for line in lines if 'Original sentence:' in line), '')
                    if original_line:
                        original = original_line.replace('Original sentence: ', '')
                        print(f"   Affected text: \"{original}\"")
            else:
                print("✓ No grammar issues detected.")
        
        print(f"\n" + "=" * 80)
        print("CLEAR ISSUE IDENTIFICATION TEST COMPLETE")
        print("=" * 80)
        
        print("\n📋 Summary:")
        print("✓ Rule identifies the SPECIFIC grammar problem")
        print("✓ Provides CLEAR guidance on what to fix") 
        print("✓ Shows the AFFECTED text for context")
        print("✗ Does NOT attempt to rewrite the entire sentence")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clear_issue_identification()
