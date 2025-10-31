#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import enhanced_enrich_issue_with_solution, _fix_title_case_issues

def test_specific_user_case():
    """Test the specific case reported by user"""
    
    # Your exact case
    test_case = {
        "message": "Avoid passive voice in sentence: 'The following requirement must be met:'",
        "context": "The following requirement must be met:",
        "issue_type": "passive_voice"
    }
    
    print("🔍 Testing Specific User Case")
    print("=" * 60)
    print(f"Input: {test_case['context']}")
    print(f"Issue: {test_case['message']}")
    print("-" * 60)
    
    # Test the title case function directly first
    print("\n1. Testing title case protection function directly:")
    test_inputs = [
        "The following requirement must be met:",
        "The Following Requirement Must Be Met:",
        "The Following Requirement Must Be Met"  # Without colon
    ]
    
    for inp in test_inputs:
        result = _fix_title_case_issues(inp)
        print(f"  Input:  '{inp}'")
        print(f"  Output: '{result}'")
        if result != inp:
            print("  ✅ Fixed")
        else:
            print("  → No change")
        print()
    
    # Test through the full system
    print("2. Testing through full enhanced RAG system:")
    try:
        result = enhanced_enrich_issue_with_solution(test_case)
        suggested_text = result.get("proposed_rewrite", test_case["context"])
        
        print(f"Result: '{suggested_text}'")
        print(f"Method: {result.get('method', 'unknown')}")
        
        # Check for title case
        words = suggested_text.split()
        title_case_words = []
        for i, word in enumerate(words):
            if i > 0 and word and len(word) > 1 and word[0].isupper() and word[1:].islower():
                if word.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from']:
                    title_case_words.append(word)
        
        if title_case_words:
            print(f"⚠️ TITLE CASE STILL DETECTED: {title_case_words}")
        else:
            print("✅ Title case properly handled")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_user_case()
