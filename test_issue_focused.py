#!/usr/bin/env python3
"""Test the issue-focused AI suggestion system."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_issue_focused_suggestions():
    """Test that AI suggestions provide solutions to specific issues."""
    try:
        from app.enhanced_rag_complete import get_enhanced_suggestion
        
        test_cases = [
            {
                "sentence": "The report was written by the team.",
                "issue_type": "passive_voice",
                "expected_solution": "should convert to active voice"
            },
            {
                "sentence": "There are many complex issues that need to be carefully addressed in this comprehensive document that was created by our experienced development team and should definitely be reviewed thoroughly by all stakeholders.",
                "issue_type": "long_sentence", 
                "expected_solution": "should break into shorter sentences"
            },
            {
                "sentence": "The system can be used to process documents effectively.",
                "issue_type": "modal_verb",
                "expected_solution": "should use more direct language"
            },
            {
                "sentence": "This is a very good solution that really works quite well.",
                "issue_type": "weak_word",
                "expected_solution": "should remove weak intensifiers"
            },
            {
                "sentence": "There are three main issues with this approach.",
                "issue_type": "wordy",
                "expected_solution": "should use more direct construction"
            }
        ]
        
        print("Testing Issue-Focused AI Suggestions...")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['issue_type'].upper()} ISSUE")
            print(f"Problem: {test_case['sentence']}")
            print(f"Expected: {test_case['expected_solution']}")
            print("-" * 40)
            
            try:
                result = get_enhanced_suggestion(
                    issue_text=test_case['sentence'],
                    issue_type=test_case['issue_type'],
                    context="Technical documentation review"
                )
                
                if result and isinstance(result, dict):
                    solution = result.get('enhanced_response', 'No solution generated')
                    method = result.get('method', 'unknown')
                    processing_time = result.get('processing_time', 0)
                    
                    print(f"✓ METHOD: {method}")
                    print(f"✓ SOLUTION: {solution}")
                    print(f"✓ TIME: {processing_time:.2f}s")
                    
                    # Check if it's actually different and addresses the issue
                    if solution.strip() != test_case['sentence'].strip():
                        if test_case['issue_type'] == 'passive_voice' and ' by ' not in solution:
                            print("✓ SUCCESS: Converted to active voice")
                        elif test_case['issue_type'] == 'long_sentence' and len(solution.split()) < len(test_case['sentence'].split()):
                            print("✓ SUCCESS: Made sentence shorter")
                        elif test_case['issue_type'] == 'modal_verb' and 'can be' not in solution:
                            print("✓ SUCCESS: Removed modal verb construction")
                        elif test_case['issue_type'] == 'weak_word' and not any(weak in solution.lower() for weak in ['very', 'really', 'quite']):
                            print("✓ SUCCESS: Removed weak words")
                        elif test_case['issue_type'] == 'wordy' and not solution.startswith('There are'):
                            print("✓ SUCCESS: Made construction more direct")
                        else:
                            print("✓ PARTIAL: Generated different text")
                    else:
                        print("✗ FAILED: Returned identical text")
                        
                else:
                    print(f"✗ FAILED: Invalid result type: {type(result)}")
                    
            except Exception as e:
                print(f"✗ ERROR: {e}")
        
        print("\n" + "=" * 60)
        
    except ImportError as e:
        print(f"✗ IMPORT ERROR: {e}")
    except Exception as e:
        print(f"✗ GENERAL ERROR: {e}")

if __name__ == "__main__":
    test_issue_focused_suggestions()
