#!/usr/bin/env python3
"""Test the simple rewriter system."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_simple_rewriter():
    """Test the simple sentence rewriter."""
    try:
        from app.simple_rewriter import get_simple_rewrite
        
        test_cases = [
            {
                "sentence": "The report was written by the team.",
                "issue_type": "passive_voice",
                "expected_change": "active voice"
            },
            {
                "sentence": "There are many issues that need to be addressed in this document that was created by the development team and should be reviewed carefully.",
                "issue_type": "long_sentence", 
                "expected_change": "shorter sentences"
            },
            {
                "sentence": "The system can be used to process documents.",
                "issue_type": "modal_verb",
                "expected_change": "more direct language"
            },
            {
                "sentence": "This is a very good solution that really works well.",
                "issue_type": "clarity",
                "expected_change": "remove weak words"
            }
        ]
        
        print("Testing Simple Sentence Rewriter...")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['issue_type']}")
            print(f"Original: {test_case['sentence']}")
            print("-" * 30)
            
            rewritten = get_simple_rewrite(test_case['sentence'], test_case['issue_type'])
            print(f"Rewritten: {rewritten}")
            
            # Check if it's actually different from original
            if rewritten.strip() != test_case['sentence'].strip():
                print("✓ SUCCESS: Generated different text")
            else:
                print("✗ FAILED: Returned identical text")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_rewriter()
