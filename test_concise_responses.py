#!/usr/bin/env python3
"""
Test the new concise AI responses
"""

import sys
import os
sys.path.append('app')

def test_concise_responses():
    """Test the new concise AI suggestion responses"""
    try:
        from ai_improvement import get_enhanced_ai_suggestion
        
        print("🔍 Testing New Concise AI Responses...\n")
        print("=" * 50)
        
        # Test case 1: Passive voice
        print("📝 Test: Passive Voice")
        print("Issue: Passive voice detected")
        print("Sentence: 'The document was written by the team'")
        print("-" * 40)
        
        result1 = get_enhanced_ai_suggestion(
            feedback_text="Passive voice detected",
            sentence_context="The document was written by the team.",
            document_type="general"
        )
        
        print(f"Method: {result1.get('method', 'unknown')}")
        print(f"Suggestion: {result1.get('suggestion', 'No suggestion')}")
        if 'gemini_answer' in result1:
            print(f"Gemini Answer: {result1['gemini_answer']}")
        print("✅ Using Gemini AI" if result1.get('method') == 'gemini_rag' else "⚠️ Using fallback")
        print()
        
        # Test case 2: Modal verb
        print("📝 Test: Modal Verb Issue")
        print("Issue: Modal verb usage: 'may' for permission")
        print("Sentence: 'You may use this feature when needed'")
        print("-" * 40)
        
        result2 = get_enhanced_ai_suggestion(
            feedback_text="Modal verb usage: 'may' for permission",
            sentence_context="You may use this feature when needed",
            document_type="general"
        )
        
        print(f"Method: {result2.get('method', 'unknown')}")
        print(f"Suggestion: {result2.get('suggestion', 'No suggestion')}")
        if 'gemini_answer' in result2:
            print(f"Gemini Answer: {result2['gemini_answer']}")
        print("✅ Using Gemini AI" if result2.get('method') == 'gemini_rag' else "⚠️ Using fallback")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_concise_responses()
