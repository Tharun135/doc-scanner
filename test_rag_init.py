#!/usr/bin/env python3
"""Test RAG system initialization."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_rag_initialization():
    """Test if RAG components can be initialized."""
    print("Testing RAG System Initialization...")
    print("=" * 50)
    
    # Test 1: Import basic dependencies
    try:
        import llama_index
        print("✓ llama_index imported successfully")
    except ImportError as e:
        print(f"✗ llama_index import failed: {e}")
        return
        
    # Test 2: Import specific components
    try:
        from llama_index.core import VectorStoreIndex
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.ollama import OllamaEmbedding
        print("✓ LlamaIndex components imported successfully")
    except ImportError as e:
        print(f"✗ LlamaIndex components import failed: {e}")
        return
    
    # Test 3: Test Ollama connection with tinyllama
    try:
        print("\nTesting Ollama connection with tinyllama...")
        llm = Ollama(model="tinyllama", request_timeout=30.0)
        
        # Test if we can get a simple response
        response = llm.complete("Hello, respond with just 'working'")
        print(f"✓ Ollama response: {str(response).strip()}")
        
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
        return
    
    # Test 4: Test the Enhanced RAG class initialization
    try:
        from app.enhanced_rag_complete import EnhancedRAGSystem
        rag_system = EnhancedRAGSystem()
        
        print(f"\n✓ EnhancedRAGSystem created")
        print(f"  - Is initialized: {rag_system.is_initialized}")
        print(f"  - LLM available: {rag_system.llm is not None}")
        print(f"  - Vector store available: {rag_system.vector_store is not None}")
        
        if not rag_system.is_initialized:
            print("Attempting manual initialization...")
            rag_system.initialize_rag()
            print(f"  - After manual init: {rag_system.is_initialized}")
            
    except Exception as e:
        print(f"✗ EnhancedRAGSystem initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_initialization()
