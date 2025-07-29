#!/usr/bin/env python3
"""
Debug RAG system availability
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_rag_system():
    """Test RAG system initialization and availability"""
    print("🔍 Debugging RAG System...")
    print("=" * 50)
    
    # Check environment
    api_key = os.getenv('GOOGLE_API_KEY')
    print(f"Google API Key present: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    
    # Test imports
    try:
        print("\n📦 Testing imports...")
        import google.generativeai as genai
        print("✅ google.generativeai imported")
        
        from langchain_google_genai import GoogleGenerativeAI
        print("✅ langchain_google_genai imported")
        
        from app.rag_system import rag_system, get_rag_suggestion
        print("✅ RAG system imported")
        
        # Test RAG system initialization
        print(f"\nRAG System initialized: {rag_system.is_initialized}")
        print(f"RAG System available: {rag_system.is_available()}")
        
        if rag_system.is_available():
            print("\n🧪 Testing RAG suggestion...")
            result = get_rag_suggestion(
                feedback_text="Passive voice detected",
                sentence_context="The document was reviewed by the team",
                document_type="technical"
            )
            
            if result:
                print("✅ RAG suggestion generated successfully")
                print(f"Method: {result.get('method')}")
                print(f"Suggestion: {result.get('suggestion', '')[:100]}...")
            else:
                print("❌ No RAG suggestion generated")
        else:
            print("❌ RAG system not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_system()
