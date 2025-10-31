#!/usr/bin/env python3
"""
Working Ollama RAG Test - Uses actual available models
"""

import sys
import subprocess
import json
import time

# Add current directory to path
sys.path.append('.')

def get_full_model_names():
    """Get full model names with tags"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]  # This includes the tag
                        models.append(model_name)
            return models
    except Exception as e:
        print(f"Error getting models: {e}")
    
    return []

def test_basic_ollama_llm(model_name):
    """Test basic Ollama LLM without embeddings first"""
    print(f"🔧 Testing basic LLM: {model_name}")
    
    try:
        from llama_index.llms.ollama import Ollama
        
        # Test basic LLM
        llm = Ollama(model=model_name, request_timeout=30.0, temperature=0.1)
        
        # Simple test query
        response = llm.complete("Rewrite this sentence in active voice: The report was written by John.")
        
        print(f"✅ LLM response: {str(response)[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def test_simple_rag_without_embeddings(model_name):
    """Test RAG using just the LLM model for both chat and embeddings"""
    print(f"🧪 Testing simple RAG: {model_name}")
    
    try:
        from llama_index.core import VectorStoreIndex, Document, Settings
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.ollama import OllamaEmbedding
        import chromadb
        
        # Initialize components
        llm = Ollama(model=model_name, request_timeout=30.0)
        
        # Use the same model for embeddings (this often works)
        embed_model = OllamaEmbedding(model_name=model_name)
        
        # Set settings
        Settings.llm = llm
        Settings.embed_model = embed_model
        
        # Create simple documents
        docs = [
            Document(text="Convert passive voice to active voice for clearer writing. Example: Change 'was written by' to 'wrote'."),
            Document(text="Use active voice instead of passive voice in technical documentation."),
            Document(text="Rewrite sentences to put the actor first, then the action.")
        ]
        
        # Create index
        print("Creating vector index...")
        index = VectorStoreIndex.from_documents(docs)
        
        # Create query engine
        query_engine = index.as_query_engine(similarity_top_k=2)
        
        # Test query
        print("Testing query...")
        response = query_engine.query("How do I fix passive voice in: 'The document was written by John'?")
        
        result = {
            "suggestion": str(response),
            "method": "ollama_simple_rag",
            "model": model_name,
            "confidence": "medium"
        }
        
        print(f"✅ RAG working!")
        print(f"Response: {result['suggestion'][:150]}...")
        return result
        
    except Exception as e:
        print(f"❌ Simple RAG failed: {e}")
        return None

def main():
    """Test with actual available models"""
    print("🚀 Working Ollama RAG Test")
    print("=" * 40)
    
    # Get full model names
    models = get_full_model_names()
    print(f"Available models: {models}")
    
    if not models:
        print("❌ No models found")
        return
    
    # Test each model
    for model in models:
        print(f"\n{'='*50}")
        print(f"Testing: {model}")
        print('='*50)
        
        # Test basic LLM first
        if test_basic_ollama_llm(model):
            # Test simple RAG
            rag_result = test_simple_rag_without_embeddings(model)
            if rag_result:
                print(f"\n🎉 SUCCESS: {model} works for RAG!")
                print("=" * 40)
                print(f"Model: {rag_result['model']}")
                print(f"Method: {rag_result['method']}")
                print(f"Confidence: {rag_result['confidence']}")
                print(f"Full response: {rag_result['suggestion']}")
                
                # Now test integration with DocScanner
                print(f"\n🔧 Testing DocScanner integration...")
                test_docscanner_integration(model, rag_result)
                break
        
        print(f"❌ {model} didn't work, trying next...")
    else:
        print("\n❌ No working models found")

def test_docscanner_integration(model, rag_result):
    """Test integration with DocScanner rule system"""
    try:
        # Create a simple DocScanner-like suggestion
        suggestion = f"🤖 Ollama RAG Enhanced: {rag_result['suggestion'][:100]}..."
        
        print(f"✅ DocScanner integration preview:")
        print(f"   Original: 'The document was written by John.'")  
        print(f"   Issue: Passive voice detected")
        print(f"   AI Suggestion: {suggestion}")
        print(f"   Powered by: {model} (Local)")
        print(f"   🏠 Private • ⚡ Fast • 💰 Free")
        
        return True
        
    except Exception as e:
        print(f"❌ DocScanner integration failed: {e}")
        return False

if __name__ == "__main__":
    main()
