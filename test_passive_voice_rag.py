#!/usr/bin/env python3
"""Test script to check RAG retrieval for passive voice knowledge."""

def test_passive_voice_rag():
    """Test if RAG can retrieve passive voice conversion knowledge."""
    print("🔍 Testing RAG Retrieval for Passive Voice Knowledge")
    print("=" * 55)
    
    try:
        # Initialize RAG system
        from app.rag_routes import retriever, init_rag_system
        print("📚 Initializing RAG system...")
        init_success = init_rag_system()
        print(f"✅ RAG initialization: {'Success' if init_success else 'Failed'}")
        
        if not retriever:
            print("❌ Retriever not available")
            return
            
        # Test queries related to passive voice
        test_queries = [
            "passive voice conversion examples",
            "convert passive to active voice",
            "must be created active voice",
            "passive voice detected examples",
            "active voice conversion steps"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: '{query}'")
            try:
                results = retriever.search(query, k=3)
                if results:
                    print(f"   Found {len(results)} results:")
                    for j, result in enumerate(results, 1):
                        score = result.get('score', 0)
                        content = result.get('content', '')[:200]
                        print(f"   {j}. Score: {score:.3f}")
                        print(f"      Content: {content}...")
                        print()
                else:
                    print("   No results found")
            except Exception as e:
                print(f"   Error: {e}")
        
        # Test specific passive voice sentence
        print("\n🎯 Testing specific sentence: 'A data source must be created'")
        query = "A data source must be created passive voice active voice conversion"
        try:
            results = retriever.search(query, k=5)
            if results:
                print(f"Found {len(results)} relevant results:")
                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    content = result.get('content', '')
                    print(f"{i}. Score: {score:.3f}")
                    print(f"   Content: {content[:300]}...")
                    print()
            else:
                print("No relevant results found for the specific sentence")
        except Exception as e:
            print(f"Error searching: {e}")
            
    except Exception as e:
        print(f"❌ Error during RAG test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_passive_voice_rag()