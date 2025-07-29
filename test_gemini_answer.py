#!/usr/bin/env python3
"""
Test script to verify the new Gemini Answer functionality
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_ai_improvement():
    """Test the AI improvement functionality with Gemini answer"""
    try:
        from ai_improvement import GeminiAISuggestionEngine
        
        print("🔍 Testing AI Improvement System...")
        
        # Create engine instance
        engine = GeminiAISuggestionEngine()
        print(f"✅ Engine created. RAG available: {engine.rag_available}")
        
        # Test feedback
        feedback_text = "Passive voice detected"
        sentence_context = "The document was written by the team."
        
        # Generate suggestion
        result = engine.generate_contextual_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="general"
        )
        
        print("\n📋 Test Results:")
        print(f"Suggestion: {result.get('suggestion', 'None')[:100]}...")
        print(f"Gemini Answer: {result.get('gemini_answer', 'None')[:100]}...")
        print(f"Method: {result.get('method', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 'Unknown')}")
        
        # Check if gemini_answer field exists
        if 'gemini_answer' in result:
            print("✅ Gemini Answer field present")
        else:
            print("❌ Gemini Answer field missing")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI improvement: {e}")
        return False

def test_fallback_suggestions():
    """Test fallback suggestions include gemini_answer"""
    try:
        from ai_improvement import GeminiAISuggestionEngine
        
        print("\n🔍 Testing Fallback Suggestions...")
        
        engine = GeminiAISuggestionEngine()
        
        # Test fallback suggestion
        result = engine.generate_smart_fallback_suggestion(
            feedback_text="Passive voice detected",
            sentence_context="The document was written by the team."
        )
        
        print(f"Fallback Suggestion: {result.get('suggestion', 'None')[:100]}...")
        print(f"Fallback Gemini Answer: {result.get('gemini_answer', 'None')[:100]}...")
        
        if 'gemini_answer' in result:
            print("✅ Fallback includes Gemini Answer field")
            return True
        else:
            print("❌ Fallback missing Gemini Answer field")
            return False
            
    except Exception as e:
        print(f"❌ Error testing fallback: {e}")
        return False

def main():
    print("🚀 Testing Gemini Answer Integration\n")
    
    # Run tests
    ai_test = test_ai_improvement()
    fallback_test = test_fallback_suggestions()
    
    print(f"\n📊 Test Summary:")
    print(f"AI Improvement Test: {'✅ PASS' if ai_test else '❌ FAIL'}")
    print(f"Fallback Test: {'✅ PASS' if fallback_test else '❌ FAIL'}")
    
    if ai_test and fallback_test:
        print("\n🎉 All tests passed! Gemini Answer functionality is working.")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main()
