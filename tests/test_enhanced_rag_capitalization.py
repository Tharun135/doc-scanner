#!/usr/bin/env python3
"""
Test the enhanced RAG system with capitalization feedback
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_enhanced_rag_capitalization():
    """Test the enhanced RAG system with capitalization feedback"""
    
    # Test case: Capitalization issue
    issue = {
        "context": "it is in ISO 8601 Zulu format.",
        "issue_type": "style",
        "message": "Start sentences with a capital letter."
    }
    
    print(f"🔍 Testing Enhanced RAG Capitalization:")
    print(f"  Sentence: '{issue['context']}'")
    print(f"  Rule ID: '{issue['issue_type']}'")
    print(f"  Feedback: '{issue['message']}'")
    
    try:
        result = enhanced_enrich_issue_with_solution(issue)
        
        print(f"  Method: {result.get('method', 'Unknown')}")
        print(f"  AI Suggestion: '{result.get('ai_suggestion', '')}'")
        print(f"  Success: {result.get('success', False)}")
        
        # Check if it's properly capitalized
        suggestion = result.get('ai_suggestion', '')
        is_capitalized = suggestion and suggestion[0].isupper()
        has_improved_prefix = suggestion.startswith("Improved:")
        
        print(f"  ✅ Capitalized: {is_capitalized}")
        print(f"  ❌ Has 'Improved:' prefix: {has_improved_prefix}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_rag_capitalization()
