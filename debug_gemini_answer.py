#!/usr/bin/env python3
"""
Debug script to test AI suggestion generation and see if gemini_answer is included
"""

import sys
import os
sys.path.append('app')

def test_ai_suggestion_response():
    """Test the AI suggestion endpoint to see the actual response"""
    try:
        # Test the fallback suggestion system directly
        from ai_improvement import GeminiAISuggestionEngine
        
        print("🔍 Testing AI Suggestion Response...\n")
        
        engine = GeminiAISuggestionEngine()
        
        # Test case 1: Passive voice
        print("Test 1: Passive voice issue")
        result1 = engine.generate_contextual_suggestion(
            feedback_text="Passive voice detected",
            sentence_context="The document was written by the team.",
            document_type="general"
        )
        
        print(f"✅ Response keys: {list(result1.keys())}")
        print(f"✅ Has gemini_answer: {'gemini_answer' in result1}")
        if 'gemini_answer' in result1:
            print(f"✅ Gemini answer: {result1['gemini_answer'][:100]}...")
        print()
        
        # Test case 2: Direct fallback
        print("Test 2: Direct fallback suggestion")
        result2 = engine.generate_smart_fallback_suggestion(
            feedback_text="Long sentence detected",
            sentence_context="This is a very long sentence that contains many clauses and should probably be broken down into smaller, more manageable pieces for better readability."
        )
        
        print(f"✅ Fallback keys: {list(result2.keys())}")
        print(f"✅ Has gemini_answer: {'gemini_answer' in result2}")
        if 'gemini_answer' in result2:
            print(f"✅ Gemini answer: {result2['gemini_answer'][:100]}...")
        print()
        
        # Test case 3: RAG system
        print("Test 3: RAG system availability")
        from rag_system import rag_system
        print(f"✅ RAG available: {rag_system.is_available()}")
        print(f"✅ RAG initialized: {rag_system.is_initialized}")
        
        if rag_system.is_available():
            print("RAG system is available, testing direct suggestion...")
            rag_result = rag_system.get_rag_suggestion(
                feedback_text="Passive voice detected",
                sentence_context="The document was written by the team."
            )
            if rag_result:
                print(f"✅ RAG keys: {list(rag_result.keys())}")
                print(f"✅ RAG has gemini_answer: {'gemini_answer' in rag_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ai_suggestion_response()
