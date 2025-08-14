#!/usr/bin/env python3
"""Debug the exact issue object returned by passive voice detection."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.passive_voice import check as check_passive_voice

def debug_passive_voice_issue_object():
    """Debug what exactly is in the issue object from passive voice detection."""
    
    print("🔍 DEBUGGING PASSIVE VOICE ISSUE OBJECT")
    print("=" * 50)
    
    # Test with a sentence that should trigger passive voice
    test_sentence = "The document is written by John"
    print(f"Testing sentence: {repr(test_sentence)}")
    
    try:
        issues = check_passive_voice(test_sentence)
        print(f"\nFound {len(issues)} issues:")
        
        for i, issue in enumerate(issues, 1):
            print(f"\nIssue {i}:")
            print(f"  Raw issue object: {issue}")
            print(f"  Type: {type(issue)}")
            
            # Check each field explicitly
            for key in ['text', 'message', 'start', 'end', 'rule', 'method', 'context', 'sentence']:
                value = issue.get(key, '<NOT_FOUND>')
                print(f"  {key}: {repr(value)} (type: {type(value)})")
            
            # Check if 'text' field is being corrupted somehow
            text_field = issue.get('text', '')
            print(f"\n  Text field analysis:")
            print(f"    Value: {repr(text_field)}")
            print(f"    Length: {len(text_field)}")
            print(f"    First 10 chars: {repr(text_field[:10])}")
            print(f"    Type: {type(text_field)}")
            
            # Check for any encoding issues
            try:
                encoded = text_field.encode('utf-8')
                print(f"    UTF-8 encoded: {encoded}")
                decoded = encoded.decode('utf-8')
                print(f"    Decoded back: {repr(decoded)}")
            except Exception as e:
                print(f"    Encoding error: {e}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_full_document_analysis():
    """Test the full document analysis to see where the issue occurs."""
    
    print(f"\n\n🧪 TESTING FULL DOCUMENT ANALYSIS")
    print("=" * 40)
    
    from app.app import review_document, get_rules
    
    test_doc = "The document is written by John."
    print(f"Test document: {repr(test_doc)}")
    
    try:
        result = review_document(test_doc, get_rules())
        issues = result.get('issues', [])
        print(f"\nFull analysis found {len(issues)} issues:")
        
        for i, issue in enumerate(issues, 1):
            if 'passive' in issue.get('message', '').lower():
                print(f"\nPassive voice issue {i}:")
                print(f"  Raw issue: {issue}")
                
                text_field = issue.get('text', '')
                print(f"  Text field: {repr(text_field)} (len={len(text_field)})")
                
                # Check if this is where the truncation happens
                if len(text_field) <= 5:  # Suspiciously short
                    print(f"  ⚠️  WARNING: Text field is suspiciously short!")
                
    except Exception as e:
        print(f"Error in full analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_passive_voice_issue_object()
    test_full_document_analysis()
