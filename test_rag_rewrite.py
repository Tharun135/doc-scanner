#!/usr/bin/env python3
"""Test the Enhanced RAG system's sentence rewriting capabilities."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_rag_rewrite():
    """Test Enhanced RAG system's ability to rewrite sentences."""
    try:
        from app.enhanced_rag_complete import get_enhanced_suggestion
        
        # Test sentences that need rewriting
        test_cases = [
            {
                "sentence": "The report was written by the team.",
                "issue_type": "passive_voice",
                "expected_improvement": "active voice"
            },
            {
                "sentence": "There are many issues that need to be addressed in this document that was created by the development team and should be reviewed carefully.",
                "issue_type": "long_sentence", 
                "expected_improvement": "shorter sentences"
            },
            {
                "sentence": "The system can be used to process documents.",
                "issue_type": "modal_verb",
                "expected_improvement": "more direct language"
            }
        ]
        
        print("Testing Enhanced RAG Sentence Rewriting...")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['issue_type']}")
            print(f"Original: {test_case['sentence']}")
            print("-" * 30)
            
            try:
                result = get_enhanced_suggestion(
                    issue_text=test_case['sentence'],
                    issue_type=test_case['issue_type'],
                    context="Technical documentation"
                )
                
                if result and isinstance(result, dict):
                    suggestion = result.get('enhanced_response', 'No suggestion generated')
                    print(f"RAG Result: {suggestion}")
                    
                    # Check if it's actually different from original
                    if suggestion.strip() != test_case['sentence'].strip():
                        print("✓ SUCCESS: Generated different text")
                    else:
                        print("✗ FAILED: Returned identical text")
                        
                    print(f"Method: {result.get('method', 'unknown')}")
                    print(f"Processing time: {result.get('processing_time', 0):.2f}s")
                else:
                    print(f"✗ FAILED: Invalid result type: {type(result)}")
                    
            except Exception as e:
                print(f"✗ ERROR: {e}")
        
        print("\n" + "=" * 50)
        
    except ImportError as e:
        print(f"✗ IMPORT ERROR: {e}")
        print("Make sure enhanced_rag_complete.py is working correctly")
    except Exception as e:
        print(f"✗ GENERAL ERROR: {e}")

if __name__ == "__main__":
    test_rag_rewrite()
