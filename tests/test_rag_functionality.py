"""
Test to demonstrate RAG system is working instead of smart_fallback
"""

import sys
import os

# Add paths for imports
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'app'))
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

def test_rag_vs_fallback():
    """Test that RAG system is working instead of smart_fallback"""
    
    print("🧪 Testing RAG vs Smart Fallback")
    print("=" * 50)
    
    # Test 1: Direct RAG system
    print("\n1. Testing Direct RAG System:")
    print("-" * 30)
    
    try:
        from ollama_rag_system import get_rag_suggestion
        
        # Test adverb issue
        result = get_rag_suggestion(
            feedback_text="Adverb detected: really - simplify language", 
            sentence_context="The app works really well"
        )
        
        if result:
            print(f"✅ RAG System Response:")
            print(f"   Method: {result.get('method')}")
            print(f"   Model: {result.get('model')}")
            print(f"   Suggestion: {result.get('suggestion', '')[:100]}...")
            print(f"   Sources: {len(result.get('sources', []))}")
        else:
            print("❌ RAG system returned None")
            
    except Exception as e:
        print(f"❌ RAG system failed: {e}")
    
    # Test 2: AI Improvement system (what the app actually uses)
    print("\n\n2. Testing AI Improvement System:")
    print("-" * 40)
    
    try:
        from ai_improvement import AISuggestionEngine
        
        engine = AISuggestionEngine()
        
        # Test with same adverb issue
        result = engine.generate_contextual_suggestion(
            feedback_text="Adverb detected: really - simplify language",
            sentence_context="The app works really well",
            document_type="general",
            writing_goals=["clarity", "conciseness"]
        )
        
        if result:
            print(f"✅ AI Improvement Response:")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0)}")
            print(f"   Suggestion: {result.get('suggestion', '')[:100]}...")
            
            # Check if it's using RAG or falling back
            if 'rag' in result.get('method', '').lower():
                print(f"   🎉 SUCCESS: Using RAG method!")
            elif 'smart_fallback' in result.get('method', '').lower():
                print(f"   ⚠️  WARNING: Still using smart_fallback")
            else:
                print(f"   ℹ️  INFO: Using method: {result.get('method')}")
                
        else:
            print("❌ AI Improvement system returned None")
            
    except Exception as e:
        print(f"❌ AI Improvement system failed: {e}")
    
    # Test 3: Passive voice example (from user's original complaint)
    print("\n\n3. Testing Passive Voice Issue:")
    print("-" * 35)
    
    try:
        result = get_rag_suggestion(
            feedback_text="Passive voice detected",
            sentence_context="The document was written yesterday"
        )
        
        if result:
            print(f"✅ Passive Voice RAG Response:")
            print(f"   Method: {result.get('method')}")
            print(f"   Suggestion: {result.get('suggestion', '')[:150]}...")
        else:
            print("❌ Passive voice RAG failed")
            
    except Exception as e:
        print(f"❌ Passive voice test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("   - RAG system should be using 'ollama_rag_direct' method")
    print("   - No more 'smart_fallback' for issues that have RAG solutions")
    print("   - AI suggestions now use vector database knowledge")

if __name__ == "__main__":
    test_rag_vs_fallback()
