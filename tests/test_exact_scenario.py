#!/usr/bin/env python3
"""
Direct test of the exact scenario from the user's web interface.
This will help us identify why smart_fallback is still appearing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_exact_scenario():
    """
    Test the exact same scenario the user is experiencing:
    - Sentence: "The installation steps are demonstrated in a video at the following link:"
    - Issue: Avoid passive voice in sentence
    """
    
    print("🔍 EXACT SCENARIO TEST")
    print("=" * 60)
    
    # Test data from user report
    sentence = "The installation steps are demonstrated in a video at the following link:"
    feedback = "Avoid passive voice in sentence"
    
    print(f"📝 Testing exact scenario:")
    print(f"   Sentence: {sentence}")
    print(f"   Feedback: {feedback}")
    print()
    
    # Test 1: Check which methods are being called
    print("🔧 TEST 1: Import and method availability")
    try:
        from app.intelligent_ai_improvement import get_enhanced_ai_suggestion
        print("✅ intelligent_ai_improvement.get_enhanced_ai_suggestion - Available")
        
        # Check if this function is correctly imported in app.py
        from app.app import main
        print("✅ app.main blueprint - Available")
        
        # Test direct function call
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            document_type="user_manual",
            writing_goals=["clarity", "directness"],
            document_content="",
            option_number=1
        )
        
        print(f"🎯 Direct function result:")
        print(f"   Method: {result.get('method')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Confidence: {result.get('confidence')}")
        
    except Exception as e:
        print(f"❌ Error in direct function test: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 2: Check the old enhanced AI system (fallback path)
    print("🔧 TEST 2: Fallback AI system")
    try:
        from app.ai_improvement import get_enhanced_ai_suggestion as old_enhanced
        print("✅ ai_improvement.get_enhanced_ai_suggestion - Available")
        
        result = old_enhanced(
            feedback_text=feedback,
            sentence_context=sentence,
            document_type="user_manual",
            writing_goals=["clarity", "directness"],
            document_content="",
            option_number=1
        )
        
        print(f"🎯 Old system result:")
        print(f"   Method: {result.get('method')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Confidence: {result.get('confidence')}")
        
    except Exception as e:
        print(f"❌ Error in old system test: {e}")
    
    print()
    
    # Test 3: Check what specific method names are being returned
    print("🔧 TEST 3: Method name analysis")
    
    expected_new_methods = [
        "document_search_primary", 
        "document_search_extended", 
        "hybrid_document_llm", 
        "contextual_rag",
        "intelligent_analysis"
    ]
    
    unexpected_old_methods = [
        "smart_rule_based",
        "smart_fallback", 
        "enhanced_ai_suggestion",
        "deterministic_fallback"
    ]
    
    print("✅ Expected NEW methods (document-first):")
    for method in expected_new_methods:
        print(f"   - {method}")
    
    print("❌ Unexpected OLD methods (should not appear):")
    for method in unexpected_old_methods:
        print(f"   - {method}")
    
    print()
    
    # Test 4: Specific passive voice test
    print("🔧 TEST 4: Passive voice specific test")
    try:
        # Test if the document search finds passive voice solutions
        from app.document_first_ai import get_document_first_suggestion
        
        result = get_document_first_suggestion(
            feedback_text="Avoid passive voice in sentence",
            sentence_context=sentence,
            document_type="user_manual",
            writing_goals=["clarity", "directness"]
        )
        
        print(f"🎯 Document-first passive voice result:")
        print(f"   Method: {result.get('method')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Sources: {len(result.get('sources', []))} sources found")
        
        # Check if solution PDFs are being found
        ai_answer = result.get('ai_answer', '')
        if 'active voice' in ai_answer.lower():
            print("✅ Solution mentions active voice - PDF content found!")
        else:
            print("⚠️ Solution does not mention active voice")
            
    except Exception as e:
        print(f"❌ Error in passive voice test: {e}")

if __name__ == "__main__":
    test_exact_scenario()