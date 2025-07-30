#!/usr/bin/env python3
"""
Debug script to check exactly why RAG is falling back to smart fallback.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_rag_availability():
    """Debug RAG system availability step by step."""
    print("🔍 Debugging RAG System Availability")
    print("=" * 50)
    
    # Step 1: Check imports
    try:
        from app.rules.rag_rule_helper import RAG_AVAILABLE
        print(f"✅ RAG_AVAILABLE in helper: {RAG_AVAILABLE}")
    except Exception as e:
        print(f"❌ Error importing RAG_AVAILABLE: {e}")
        return
    
    if not RAG_AVAILABLE:
        print("❌ RAG marked as unavailable in rag_rule_helper.py")
        return
    
    # Step 2: Check RAG system import
    try:
        from app.rag_system import get_rag_suggestion, rag_system
        print("✅ RAG system import successful")
    except Exception as e:
        print(f"❌ RAG system import failed: {e}")
        return
    
    # Step 3: Check global RAG instance
    print(f"🔧 Global rag_system object: {rag_system}")
    print(f"🔧 rag_system.is_initialized: {getattr(rag_system, 'is_initialized', 'NOT FOUND')}")
    
    # Step 4: Check availability method
    try:
        is_available = rag_system.is_available()
        print(f"🎯 rag_system.is_available(): {is_available}")
    except Exception as e:
        print(f"❌ Error checking is_available(): {e}")
    
    # Step 5: Check individual components
    try:
        print(f"🔧 LANGCHAIN_AVAILABLE: {getattr(rag_system, 'LANGCHAIN_AVAILABLE', 'NOT FOUND')}")
        print(f"🔧 is_initialized: {getattr(rag_system, 'is_initialized', 'NOT FOUND')}")
        print(f"🔧 llm: {getattr(rag_system, 'llm', 'NOT FOUND')}")
        print(f"🔧 embeddings: {getattr(rag_system, 'embeddings', 'NOT FOUND')}")
        print(f"🔧 vectorstore: {getattr(rag_system, 'vectorstore', 'NOT FOUND')}")
        print(f"🔧 retrieval_qa: {getattr(rag_system, 'retrieval_qa', 'NOT FOUND')}")
    except Exception as e:
        print(f"❌ Error checking components: {e}")
    
    # Step 6: Test direct RAG call
    print("\n🧪 Testing Direct RAG Call")
    print("-" * 30)
    try:
        result = get_rag_suggestion(
            feedback_text="passive voice test",
            sentence_context="The document was written by John",
            document_type="technical"
        )
        print(f"📊 Direct RAG result: {result}")
        
        if result:
            print("✅ RAG system working!")
        else:
            print("⚠️  RAG returned None - likely API quota or initialization issue")
            
    except Exception as e:
        print(f"❌ Direct RAG call failed: {e}")
    
    # Step 7: Check rule knowledge base
    print(f"\n📚 Rule Knowledge Base Check")
    print("-" * 30)
    try:
        has_rule_kb = hasattr(rag_system, 'rule_vectorstore') and rag_system.rule_vectorstore
        print(f"🔧 Has rule_vectorstore: {has_rule_kb}")
        
        if has_rule_kb:
            print("✅ Rule knowledge base loaded")
        else:
            print("⚠️  Rule knowledge base not loaded")
            
    except Exception as e:
        print(f"❌ Error checking rule knowledge base: {e}")

def test_passive_voice_specifically():
    """Test the exact passive voice scenario from user's example."""
    print("\n🎯 Testing Passive Voice Rule Specifically")
    print("=" * 45)
    
    test_content = """The migration from SIMATIC S7 Connector to SIMATIC S7+ Connector is only supported for S7-1200/1500 controllers that are configured with Optimized S7-Protocol."""
    
    try:
        from app.rules.passive_voice import check
        print("✅ Passive voice rule imported successfully")
        
        print(f"📝 Test content: {test_content}")
        results = check(test_content)
        
        print(f"📊 Results count: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"   {i}. Method: {result.get('method', 'N/A')}")
            print(f"      Text: '{result.get('text', 'N/A')}'")
            print(f"      Message: {result.get('message', 'N/A')[:100]}...")
            
    except Exception as e:
        print(f"❌ Error testing passive voice: {e}")

if __name__ == "__main__":
    debug_rag_availability()
    test_passive_voice_specifically()
    
    print("\n📋 Summary")
    print("=" * 15)
    print("Most likely causes for smart fallback:")
    print("1. 🚫 Google API quota exceeded (50/day limit)")
    print("2. 🔧 RAG system initialization issue")
    print("3. 🌐 Network connectivity to Google API")
    print("4. 🔑 API key configuration issue")
