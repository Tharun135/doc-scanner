#!/usr/bin/env python3
"""
Test document-first AI system directly to debug the issue.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_document_first_ai():
    """Test the document-first AI system directly."""
    
    print("🔧 Testing document-first AI system...")
    
    try:
        from app.document_first_ai import get_document_first_suggestion
        print("✅ Successfully imported document_first_ai")
        
        # Test case: passive voice
        feedback_text = "Avoid passive voice in sentence"
        sentence_context = "The installation steps are demonstrated in a video at the following link:"
        document_type = "user_manual"
        
        print(f"📝 Testing with:")
        print(f"   Feedback: {feedback_text}")
        print(f"   Sentence: {sentence_context}")
        
        result = get_document_first_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=["clarity", "directness"]
        )
        
        print(f"🎯 Result:")
        print(f"   Method: {result.get('method')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   AI Answer: {result.get('ai_answer', '')[:100]}...")
        print(f"   Sources: {len(result.get('sources', []))} sources")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing document-first AI: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_intelligent_ai_suggestion():
    """Test the intelligent AI suggestion system that should use document-first."""
    
    print("\n🔧 Testing intelligent AI suggestion system...")
    
    try:
        from app.intelligent_ai_improvement import get_enhanced_ai_suggestion
        print("✅ Successfully imported intelligent_ai_improvement")
        
        # Test case: passive voice
        feedback_text = "Avoid passive voice in sentence"
        sentence_context = "The installation steps are demonstrated in a video at the following link:"
        document_type = "user_manual"
        
        print(f"📝 Testing with:")
        print(f"   Feedback: {feedback_text}")
        print(f"   Sentence: {sentence_context}")
        
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=["clarity", "directness"],
            document_content="",
            option_number=1
        )
        
        print(f"🎯 Result:")
        print(f"   Method: {result.get('method')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   AI Answer: {result.get('ai_answer', '')[:100]}...")
        print(f"   Sources: {len(result.get('sources', []))} sources")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing intelligent AI: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Testing Document-First AI System\n")
    
    # Test 1: Document-first AI directly
    doc_result = test_document_first_ai()
    
    # Test 2: Intelligent AI suggestion (should use document-first)
    intelligent_result = test_intelligent_ai_suggestion()
    
    print("\n" + "="*60)
    print("📊 SUMMARY:")
    print("="*60)
    
    if doc_result:
        print(f"✅ Document-First AI: {doc_result.get('method')} ({doc_result.get('confidence')})")
    else:
        print("❌ Document-First AI: Failed")
        
    if intelligent_result:
        print(f"✅ Intelligent AI: {intelligent_result.get('method')} ({intelligent_result.get('confidence')})")
    else:
        print("❌ Intelligent AI: Failed")
        
    # Expected: Both should return document-first methods, not smart_fallback
    expected_methods = ["document_search_primary", "document_search_extended", "hybrid_document_llm", "intelligent_analysis"]
    
    if intelligent_result and intelligent_result.get('method') in expected_methods:
        print("🎉 SUCCESS: System is using document-first methods!")
    else:
        print("⚠️ ISSUE: System not using document-first methods")