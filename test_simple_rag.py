"""
Simple RAG test using direct Ollama API calls instead of LlamaIndex
"""
import requests
import json
import chromadb
import os

def test_simple_ollama_rag():
    """Test RAG using direct Ollama calls instead of LlamaIndex"""
    
    print("🧪 Testing Simple Ollama RAG")
    print("=" * 40)
    
    # Test Ollama directly with small model
    ollama_url = "http://localhost:11434/api/generate"
    
    # Test 1: Simple model test
    print("\n1. Testing direct Ollama API...")
    response = requests.post(ollama_url, json={
        'model': 'phi3:mini',
        'prompt': 'Say "Hello from phi3"',
        'stream': False
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Ollama API working: {result['response'][:50]}...")
    else:
        print(f"❌ Ollama API failed: {response.text}")
        return
    
    # Test 2: ChromaDB access
    print("\n2. Testing ChromaDB access...")
    try:
        chroma_path = os.path.expanduser("./chroma_db")
        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_collection("docscanner_solutions")
        print(f"✅ ChromaDB collection loaded with {collection.count()} documents")
        
        # Test query
        results = collection.query(
            query_texts=["adverb really well"],
            n_results=2
        )
        print(f"✅ ChromaDB query successful, found {len(results['documents'][0])} results")
        for i, doc in enumerate(results['documents'][0]):
            print(f"   - Result {i+1}: {doc[:100]}...")
    except Exception as e:
        print(f"❌ ChromaDB failed: {e}")
        return
    
    # Test 3: Combined RAG
    print("\n3. Testing combined RAG flow...")
    try:
        # Query ChromaDB for relevant context
        query_text = "The app works really well - adverb issue"
        results = collection.query(
            query_texts=[query_text],
            n_results=2
        )
        
        context = "\n".join(results['documents'][0])
        
        # Create RAG prompt
        rag_prompt = f"""You are a writing improvement assistant. Based on the following context about writing rules, provide a suggestion for improving this sentence.

CONTEXT:
{context[:500]}...

USER REQUEST: The app works really well
ISSUE: Contains unnecessary adverb "really"

Please provide a concise improvement suggestion:"""

        # Send to Ollama
        response = requests.post(ollama_url, json={
            'model': 'phi3:mini',
            'prompt': rag_prompt,
            'stream': False
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ RAG suggestion: {result['response']}")
            return result['response']
        else:
            print(f"❌ RAG failed: {response.text}")
    
    except Exception as e:
        print(f"❌ Combined RAG failed: {e}")

if __name__ == "__main__":
    test_simple_ollama_rag()
