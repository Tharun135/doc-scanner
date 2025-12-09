#!/usr/bin/env python3
"""
Test ChromaDB collection availability.
"""

def test_chromadb():
    """Test if ChromaDB collection is available."""
    
    print("🔍 TESTING CHROMADB COLLECTION")
    print("=" * 30)
    
    try:
        from app.services.enrichment import _get_collection, _cached_vector_query
        
        print("✅ Successfully imported enrichment functions")
        
        # Test collection
        col = _get_collection()
        
        if col:
            print("✅ ChromaDB collection is available")
            
            # Test query
            query_results = _cached_vector_query("passive voice detected by rule", n_results=2)
            
            if query_results:
                print("✅ Vector query works")
                print(f"   Documents: {len(query_results.get('documents', [[]]))}") 
                print(f"   First doc preview: {query_results['documents'][0][0][:100] if query_results.get('documents') and query_results['documents'][0] else 'None'}...")
                
                if query_results.get('metadatas') and query_results['metadatas'][0]:
                    print(f"   First metadata: {query_results['metadatas'][0][0]}")
                else:
                    print("❌ No metadata available")
            else:
                print("❌ Vector query failed")
        else:
            print("❌ ChromaDB collection NOT available")
            
    except Exception as e:
        print(f"❌ Error testing ChromaDB: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def test_ollama_direct():
    """Test Ollama direct call."""
    
    print(f"\n🔍 TESTING OLLAMA DIRECT")
    print("=" * 25)
    
    try:
        import requests
        
        # Test Ollama availability
        response = requests.get('http://localhost:11434/api/version', timeout=2)
        if response.status_code == 200:
            print("✅ Ollama service is available")
            print(f"   Version: {response.json()}")
            
            # Test simple generation
            gen_response = requests.post('http://localhost:11434/api/generate', json={
                'model': 'tinyllama:latest',
                'prompt': 'Fix passive voice: The file was saved.',
                'stream': False,
                'options': {
                    'num_predict': 20,
                    'temperature': 0.1
                }
            }, timeout=10)
            
            if gen_response.status_code == 200:
                result = gen_response.json()
                print("✅ Ollama generation works")
                print(f"   Response: '{result.get('response', '')[:100]}...'")
            else:
                print(f"❌ Ollama generation failed: {gen_response.status_code}")
        else:
            print(f"❌ Ollama not available: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")

if __name__ == "__main__":
    test_chromadb()
    test_ollama_direct()
    
    print(f"\n💡 Both ChromaDB and Ollama need to work for ollama_rag_direct to succeed")
